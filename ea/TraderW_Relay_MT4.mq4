#property strict

input string InpServerUrl = "http://127.0.0.1";
input string InpApiKey = "";
input int InpIntervalSeconds = 10;
input int InpTimeoutMs = 15000;
input int InpPostRetryCount = 5;
input int InpRetryDelayMs = 500;
input int InpSlippage = 5;
input bool InpDebug = false;

string JsonEscape(string s)
{
  StringReplace(s, "\\", "\\\\");
  StringReplace(s, "\"", "\\\"");
  StringReplace(s, "\r", "\\r");
  StringReplace(s, "\n", "\\n");
  StringReplace(s, "\t", "\\t");
  return s;
}

string ToIso8601(datetime t)
{
  if (t <= 0)
  {
    datetime g = TimeGMT();
    if (g > 0) t = g;
    else t = TimeCurrent();
  }
  MqlDateTime dt;
  TimeToStruct(t, dt);
  return StringFormat("%04d-%02d-%02dT%02d:%02d:%02dZ", dt.year, dt.mon, dt.day, dt.hour, dt.min, dt.sec);
}

string UrlEncode(string s)
{
  string out = "";
  int n = StringLen(s);
  for (int i = 0; i < n; i++)
  {
    ushort c = StringGetCharacter(s, i);
    if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '-' || c == '_' || c == '.' || c == '~')
      out += CharToString((uchar)c);
    else if (c == ' ')
      out += "%20";
    else
      out += StringFormat("%%%02X", c);
  }
  return out;
}

int ParseHttpStatusLoose(string headers)
{
  int p = StringFind(headers, "HTTP/", 0);
  if (p < 0) p = StringFind(headers, "http/", 0);
  if (p < 0) return 0;
  int n = StringLen(headers);
  for (int i = p; i < n - 2; i++)
  {
    ushort c0 = StringGetCharacter(headers, i);
    ushort c1 = StringGetCharacter(headers, i + 1);
    ushort c2 = StringGetCharacter(headers, i + 2);
    if (c0 >= '0' && c0 <= '9' && c1 >= '0' && c1 <= '9' && c2 >= '0' && c2 <= '9')
      return (int)StringToInteger(StringSubstr(headers, i, 3));
  }
  return 0;
}

bool HttpRequest(string method, string url, string body, string &response, int &status)
{
  char data[];
  if (body != "")
  {
    int n = StringToCharArray(body, data, 0, WHOLE_ARRAY, CP_UTF8);
    if (n > 0) ArrayResize(data, n - 1);
  }
  else
  {
    ArrayResize(data, 0);
  }

  int body_size = (int)ArraySize(data);
  string headers =
    "Accept: application/json\r\n"
    "Content-Type: application/json\r\n"
    "X-API-Key: " + InpApiKey + "\r\n"
    "Content-Length: " + (string)body_size + "\r\n"
    "Connection: close\r\n\r\n";

  char result[];
  string result_headers;

  int attempts = 1;
  if (InpPostRetryCount > 0)
    attempts = InpPostRetryCount + 1;

  for (int i = 0; i < attempts; i++)
  {
    ArrayResize(result, 0);
    result_headers = "";
    ResetLastError();
    int res = WebRequest(method, url, headers, InpTimeoutMs, data, result, result_headers);
    int le = GetLastError();
    int resp_bytes = (int)ArraySize(result);
    int hdr_len = StringLen(result_headers);

    if (res == -1 || (le == 5203 && resp_bytes == 0 && hdr_len == 0 && !(res >= 100 && res <= 599)))
    {
      if (InpDebug) Print("WebRequest failed method=", method, " url=", url, " res=", res, " lastError=", le, " reqBytes=", body_size);
      if (i + 1 < attempts && le == 5203)
      {
        Sleep(InpRetryDelayMs);
        continue;
      }
      status = -1;
      response = "";
      return false;
    }

    int http = 0;
    if (res >= 100 && res <= 599) http = res;
    else http = ParseHttpStatusLoose(result_headers);
    if (http == 0 && resp_bytes > 0) http = 200;
    status = http;
    response = CharArrayToString(result, 0, resp_bytes, CP_UTF8);
    if (InpDebug) Print("WebRequest ok method=", method, " url=", url, " res=", res, " http=", http, " lastError=", le, " reqBytes=", body_size, " respBytes=", resp_bytes, " hdrLen=", hdr_len);
    return true;
  }

  status = -1;
  response = "";
  return false;
}

bool ExtractJsonObjects(string arrayJson, string &objs[])
{
  ArrayResize(objs, 0);
  int len = StringLen(arrayJson);
  int depth = 0;
  int start = -1;
  for (int i = 0; i < len; i++)
  {
    ushort ch = StringGetCharacter(arrayJson, i);
    if (ch == '{')
    {
      if (depth == 0) start = i;
      depth++;
    }
    else if (ch == '}')
    {
      depth--;
      if (depth == 0 && start >= 0)
      {
        string obj = StringSubstr(arrayJson, start, i - start + 1);
        int sz = ArraySize(objs);
        ArrayResize(objs, sz + 1);
        objs[sz] = obj;
        start = -1;
      }
    }
  }
  return ArraySize(objs) > 0;
}

bool JsonFindString(string obj, string key, string &value)
{
  string needle = "\"" + key + "\":\"";
  int p = StringFind(obj, needle, 0);
  if (p < 0) return false;
  p += StringLen(needle);
  int q = StringFind(obj, "\"", p);
  if (q < 0) return false;
  value = StringSubstr(obj, p, q - p);
  return true;
}

bool JsonFindInt(string obj, string key, long &value)
{
  string needle = "\"" + key + "\":";
  int p = StringFind(obj, needle, 0);
  if (p < 0) return false;
  p += StringLen(needle);
  int q = p;
  int len = StringLen(obj);
  while (q < len)
  {
    ushort c = StringGetCharacter(obj, q);
    if ((c >= '0' && c <= '9') || c == '-') { q++; continue; }
    break;
  }
  string num = StringSubstr(obj, p, q - p);
  value = (long)StringToInteger(num);
  return true;
}

bool JsonFindDouble(string obj, string key, double &value)
{
  string needle = "\"" + key + "\":";
  int p = StringFind(obj, needle, 0);
  if (p < 0) return false;
  p += StringLen(needle);
  int q = p;
  int len = StringLen(obj);
  while (q < len)
  {
    ushort c = StringGetCharacter(obj, q);
    if ((c >= '0' && c <= '9') || c == '-' || c == '.' || c == 'e' || c == 'E' || c == '+') { q++; continue; }
    break;
  }
  string num = StringSubstr(obj, p, q - p);
  value = StrToDouble(num);
  return true;
}

bool ParseActions(string json, string &objs[])
{
  int k = StringFind(json, "\"actions\"", 0);
  if (k < 0) return false;
  int lb = StringFind(json, "[", k);
  int rb = StringFind(json, "]", lb);
  if (lb < 0 || rb < 0) return false;
  string arr = StringSubstr(json, lb, rb - lb + 1);
  return ExtractJsonObjects(arr, objs);
}

string BuildSyncPayload()
{
  string mt5_login = (string)AccountNumber();
  string mt5_server = AccountServer();
  string mt5_company = AccountCompany();
  string currency = AccountCurrency();
  double balance = AccountBalance();
  double equity = AccountEquity();
  double margin = AccountMargin();
  double margin_free = AccountFreeMargin();
  double margin_level = 0;
  if (margin > 0) margin_level = (equity / margin) * 100.0;
  double profit = AccountProfit();

  string json = "{";
  json += "\"mt5_account\":{";
  json += "\"platform\":\"mt4\",";
  json += "\"mt5_login\":\"" + JsonEscape(mt5_login) + "\",";
  json += "\"mt5_server\":\"" + JsonEscape(mt5_server) + "\",";
  json += "\"mt5_company\":\"" + JsonEscape(mt5_company) + "\",";
  json += "\"currency\":\"" + JsonEscape(currency) + "\",";
  json += "\"balance\":" + DoubleToStr(balance, 2) + ",";
  json += "\"equity\":" + DoubleToStr(equity, 2) + ",";
  json += "\"margin\":" + DoubleToStr(margin, 2) + ",";
  json += "\"margin_free\":" + DoubleToStr(margin_free, 2) + ",";
  json += "\"margin_level\":" + DoubleToStr(margin_level, 2) + ",";
  json += "\"profit\":" + DoubleToStr(profit, 2);
  json += "},";

  json += "\"orders\":[";
  bool first_order = true;
  int total = OrdersTotal();
  for (int i = 0; i < total; i++)
  {
    if (!OrderSelect(i, SELECT_BY_POS, MODE_TRADES))
      continue;

    int type = OrderType();
    if (type == OP_BUY || type == OP_SELL)
      continue;

    string symbol = OrderSymbol();
    int digits = (int)MarketInfo(symbol, MODE_DIGITS);
    double price_current = (type == OP_BUYLIMIT || type == OP_BUYSTOP) ? MarketInfo(symbol, MODE_ASK) : MarketInfo(symbol, MODE_BID);
    if (!first_order) json += ",";
    first_order = false;
    json += "{";
    json += "\"ticket\":" + (string)OrderTicket() + ",";
    json += "\"symbol\":\"" + JsonEscape(symbol) + "\",";
    json += "\"order_type\":\"" + (type == OP_BUYLIMIT ? "buy_limit" : type == OP_SELLLIMIT ? "sell_limit" : type == OP_BUYSTOP ? "buy_stop" : type == OP_SELLSTOP ? "sell_stop" : "unknown") + "\",";
    json += "\"volume\":" + DoubleToStr(OrderLots(), 2) + ",";
    json += "\"price_open\":" + DoubleToStr(OrderOpenPrice(), digits) + ",";
    json += "\"price_current\":" + DoubleToStr(price_current, digits) + ",";
    json += "\"sl\":" + DoubleToStr(OrderStopLoss(), digits) + ",";
    json += "\"tp\":" + DoubleToStr(OrderTakeProfit(), digits) + ",";
    json += "\"commission\":0,";
    json += "\"swap\":0,";
    json += "\"time_setup\":\"" + ToIso8601(OrderOpenTime()) + "\",";
    json += "\"time_done\":null";
    json += "}";
  }
  json += "],";

  json += "\"positions\":[";
  bool first_pos = true;
  for (int j = 0; j < total; j++)
  {
    if (!OrderSelect(j, SELECT_BY_POS, MODE_TRADES))
      continue;

    int type2 = OrderType();
    if (type2 != OP_BUY && type2 != OP_SELL)
      continue;

    string symbol2 = OrderSymbol();
    int digits2 = (int)MarketInfo(symbol2, MODE_DIGITS);
    double price_current2 = OrderClosePrice();
    if (price_current2 <= 0)
      price_current2 = (type2 == OP_BUY) ? MarketInfo(symbol2, MODE_BID) : MarketInfo(symbol2, MODE_ASK);
    double commission2 = OrderCommission();
    double swap2 = OrderSwap();
    double profit = OrderProfit() + OrderSwap() + OrderCommission();
    if (!first_pos) json += ",";
    first_pos = false;
    json += "{";
    json += "\"ticket\":" + (string)OrderTicket() + ",";
    json += "\"symbol\":\"" + JsonEscape(symbol2) + "\",";
    json += "\"position_type\":\"" + (type2 == OP_BUY ? "buy" : "sell") + "\",";
    json += "\"volume\":" + DoubleToStr(OrderLots(), 2) + ",";
    json += "\"price_open\":" + DoubleToStr(OrderOpenPrice(), digits2) + ",";
    json += "\"price_current\":" + DoubleToStr(price_current2, digits2) + ",";
    json += "\"sl\":" + DoubleToStr(OrderStopLoss(), digits2) + ",";
    json += "\"tp\":" + DoubleToStr(OrderTakeProfit(), digits2) + ",";
    json += "\"commission\":" + DoubleToStr(commission2, 2) + ",";
    json += "\"swap\":" + DoubleToStr(swap2, 2) + ",";
    json += "\"profit\":" + DoubleToStr(profit, 2) + ",";
    json += "\"time_open\":\"" + ToIso8601(OrderOpenTime()) + "\"";
    json += "}";
  }
  json += "],";

  json += "\"sent_at\":\"" + ToIso8601(0) + "\"";
  json += "}";
  return json;
}

bool PostActionResult(long action_id, bool ok, long error_code, string error_message)
{
  string body = "{";
  body += "\"action_id\":" + (string)action_id + ",";
  body += "\"status\":\"" + (ok ? "success" : "failed") + "\",";
  if (ok)
  {
    body += "\"error_code\":null,";
    body += "\"error_message\":null,";
  }
  else
  {
    body += "\"error_code\":" + (string)error_code + ",";
    body += "\"error_message\":\"" + JsonEscape(error_message) + "\",";
  }
  body += "\"executed_at\":\"" + ToIso8601(0) + "\"";
  body += "}";

  string resp;
  int st;
  return HttpRequest("POST", InpServerUrl + "/api/v1/mt5/action-results", body, resp, st) && (st >= 200 && st < 300);
}

void ExecuteActions()
{
  string mt5_login = (string)AccountNumber();
  string mt5_server = AccountServer();
  string url = InpServerUrl + "/api/v1/mt5/actions?mt5_login=" + UrlEncode(mt5_login) + "&mt5_server=" + UrlEncode(mt5_server) + "&platform=mt4";

  string resp;
  int st;
  if (!HttpRequest("GET", url, "", resp, st) || st < 200 || st >= 300)
    return;

  string objs[];
  if (!ParseActions(resp, objs))
    return;

  int n = ArraySize(objs);
  for (int i = 0; i < n; i++)
  {
    long action_id = 0;
    string action_type = "";
    string target_kind = "";
    long ticket = 0;
    string symbol = "";
    double volume = 0;

    if (!JsonFindInt(objs[i], "id", action_id)) continue;
    JsonFindString(objs[i], "action_type", action_type);
    JsonFindString(objs[i], "target_kind", target_kind);
    JsonFindInt(objs[i], "ticket", ticket);
    JsonFindString(objs[i], "symbol", symbol);
    JsonFindDouble(objs[i], "volume", volume);

    bool ok = false;
    long err = 0;
    string err_msg = "";

    if (action_type == "close" && target_kind == "position")
    {
      if (OrderSelect((int)ticket, SELECT_BY_TICKET, MODE_TRADES))
      {
        int tp = OrderType();
        string sym = OrderSymbol();
        double lots = OrderLots();
        double price = (tp == OP_BUY) ? MarketInfo(sym, MODE_BID) : MarketInfo(sym, MODE_ASK);
        ok = OrderClose((int)ticket, lots, price, InpSlippage, clrNONE);
        if (!ok) { err = GetLastError(); err_msg = "OrderClose failed"; ResetLastError(); }
      }
      else
      {
        ok = true;
      }
    }
    else if (action_type == "close" && target_kind == "order")
    {
      if (OrderSelect((int)ticket, SELECT_BY_TICKET, MODE_TRADES))
      {
        ok = OrderDelete((int)ticket);
        if (!ok) { err = GetLastError(); err_msg = "OrderDelete failed"; ResetLastError(); }
      }
      else
      {
        ok = true;
      }
    }
    else
    {
      ok = false;
      err = 0;
      err_msg = "unsupported action";
    }

    PostActionResult(action_id, ok, err, err_msg);
  }
}

void SyncOnce()
{
  if (InpApiKey == "" || InpServerUrl == "")
    return;

  if (InpDebug)
    Print("SyncOnce mt5_login=", (string)AccountNumber(), " mt5_server=", AccountServer(), " url=", InpServerUrl);

  string body = BuildSyncPayload();
  string resp;
  int st;
  bool ok = HttpRequest("POST", InpServerUrl + "/api/v1/mt5/sync", body, resp, st);
  if (!ok)
  {
    int le = GetLastError();
    if (le == 4014)
      Print("WebRequest 失败：URL 未被允许，请在 MT4 里 Tools -> Options -> Expert Advisors 添加 URL：", InpServerUrl);
    else
      Print("WebRequest 失败，LastError=", le);
    ResetLastError();
    return;
  }
  if (st < 200 || st >= 300)
    Print("同步失败，HTTP=", st, " resp=", resp);
}

int init()
{
  EventSetTimer(MathMax(10, InpIntervalSeconds));
  return 0;
}

int deinit()
{
  EventKillTimer();
  return 0;
}

void OnTimer()
{
  ExecuteActions();
  Sleep(100);
  SyncOnce();
}

