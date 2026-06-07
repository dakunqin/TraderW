#property strict

#include <Trade/Trade.mqh>

input string InpServerUrl = "http://127.0.0.1";
input string InpApiKey = "";
input int InpIntervalSeconds = 10;
input int InpTimeoutMs = 15000;
input int InpPostRetryCount = 5;
input int InpRetryDelayMs = 500;
input bool InpDebug = false;

CTrade trade;

string EA_VERSION = "2026-06-06-identityfix-2";

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
    datetime ts = TimeTradeServer();
    if (ts > 0) t = ts;
    else
    {
      datetime tc = TimeCurrent();
      if (tc > 0) t = tc;
      else
      {
        datetime tl = TimeLocal();
        if (tl > 0) t = tl;
        else t = (datetime)1;
      }
    }
  }

  MqlDateTime dt;
  TimeToStruct(t, dt);
  return StringFormat("%04d-%02d-%02dT%02d:%02d:%02dZ", dt.year, dt.mon, dt.day, dt.hour, dt.min, dt.sec);
}

string OrderTypeToString(long t)
{
  if (t == ORDER_TYPE_BUY) return "buy";
  if (t == ORDER_TYPE_SELL) return "sell";
  if (t == ORDER_TYPE_BUY_LIMIT) return "buy_limit";
  if (t == ORDER_TYPE_SELL_LIMIT) return "sell_limit";
  if (t == ORDER_TYPE_BUY_STOP) return "buy_stop";
  if (t == ORDER_TYPE_SELL_STOP) return "sell_stop";
  if (t == ORDER_TYPE_BUY_STOP_LIMIT) return "buy_stop_limit";
  if (t == ORDER_TYPE_SELL_STOP_LIMIT) return "sell_stop_limit";
  return "unknown";
}

bool GetMt5Identity(string &login, string &server)
{
  long lg = AccountInfoInteger(ACCOUNT_LOGIN);
  server = AccountInfoString(ACCOUNT_SERVER);
  if (lg <= 0 || server == "")
    return false;
  login = (string)lg;
  return true;
}

string PositionTypeToString(long t)
{
  if (t == POSITION_TYPE_BUY) return "buy";
  if (t == POSITION_TYPE_SELL) return "sell";
  return "unknown";
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
    if (InpDebug)
      Print("WebRequest ok method=", method, " url=", url, " res=", res, " http=", http, " lastError=", le, " reqBytes=", body_size, " respBytes=", resp_bytes, " hdrLen=", hdr_len);
    return true;
  }

  status = -1;
  response = "";
  return false;
}

string BuildSyncPayload(const string mt5_login, const string mt5_server)
{
  string mt5_company = AccountInfoString(ACCOUNT_COMPANY);
  string currency = AccountInfoString(ACCOUNT_CURRENCY);
  double balance = AccountInfoDouble(ACCOUNT_BALANCE);
  double equity = AccountInfoDouble(ACCOUNT_EQUITY);
  double margin = AccountInfoDouble(ACCOUNT_MARGIN);
  double margin_free = AccountInfoDouble(ACCOUNT_MARGIN_FREE);
  double margin_level = AccountInfoDouble(ACCOUNT_MARGIN_LEVEL);
  double profit = AccountInfoDouble(ACCOUNT_PROFIT);

  string json = "{";
  json += "\"mt5_account\":{";
  json += "\"platform\":\"mt5\",";
  json += "\"mt5_login\":\"" + JsonEscape(mt5_login) + "\",";
  json += "\"mt5_server\":\"" + JsonEscape(mt5_server) + "\",";
  json += "\"mt5_company\":\"" + JsonEscape(mt5_company) + "\",";
  json += "\"currency\":\"" + JsonEscape(currency) + "\",";
  json += "\"balance\":" + DoubleToString(balance, 2) + ",";
  json += "\"equity\":" + DoubleToString(equity, 2) + ",";
  json += "\"margin\":" + DoubleToString(margin, 2) + ",";
  json += "\"margin_free\":" + DoubleToString(margin_free, 2) + ",";
  json += "\"margin_level\":" + DoubleToString(margin_level, 2) + ",";
  json += "\"profit\":" + DoubleToString(profit, 2);
  json += "},";

  json += "\"orders\":[";
  int orders_total = OrdersTotal();
  bool first_order = true;
  for (int i = 0; i < orders_total; i++)
  {
    ulong ticket = OrderGetTicket(i);
    if (!OrderSelect(ticket))
      continue;
    string symbol = OrderGetString(ORDER_SYMBOL);
    long type = OrderGetInteger(ORDER_TYPE);
    double volume = OrderGetDouble(ORDER_VOLUME_CURRENT);
    double price_open = OrderGetDouble(ORDER_PRICE_OPEN);
    double sl = OrderGetDouble(ORDER_SL);
    double tp = OrderGetDouble(ORDER_TP);
    datetime t_setup = (datetime)OrderGetInteger(ORDER_TIME_SETUP);
    datetime t_done = (datetime)OrderGetInteger(ORDER_TIME_DONE);

    if (!first_order) json += ",";
    first_order = false;
    json += "{";
    json += "\"ticket\":" + (string)(long)ticket + ",";
    json += "\"symbol\":\"" + JsonEscape(symbol) + "\",";
    json += "\"order_type\":\"" + OrderTypeToString(type) + "\",";
    json += "\"volume\":" + DoubleToString(volume, 2) + ",";
    json += "\"price_open\":" + DoubleToString(price_open, (int)SymbolInfoInteger(symbol, SYMBOL_DIGITS)) + ",";
    json += "\"sl\":" + DoubleToString(sl, (int)SymbolInfoInteger(symbol, SYMBOL_DIGITS)) + ",";
    json += "\"tp\":" + DoubleToString(tp, (int)SymbolInfoInteger(symbol, SYMBOL_DIGITS)) + ",";
    if (t_setup > 0) json += "\"time_setup\":\"" + ToIso8601(t_setup) + "\",";
    else json += "\"time_setup\":null,";
    if (t_done > 0) json += "\"time_done\":\"" + ToIso8601(t_done) + "\"";
    else json += "\"time_done\":null";
    json += "}";
  }
  json += "],";

  json += "\"positions\":[";
  int pos_total = PositionsTotal();
  bool first_pos = true;
  for (int i = 0; i < pos_total; i++)
  {
    ulong ticket = PositionGetTicket(i);
    if (!PositionSelectByTicket(ticket))
      continue;
    string symbol = PositionGetString(POSITION_SYMBOL);
    long type = PositionGetInteger(POSITION_TYPE);
    double volume = PositionGetDouble(POSITION_VOLUME);
    double price_open = PositionGetDouble(POSITION_PRICE_OPEN);
    double sl = PositionGetDouble(POSITION_SL);
    double tp = PositionGetDouble(POSITION_TP);
    double profit = PositionGetDouble(POSITION_PROFIT);
    datetime t_open = (datetime)PositionGetInteger(POSITION_TIME);

    if (!first_pos) json += ",";
    first_pos = false;
    json += "{";
    json += "\"ticket\":" + (string)(long)ticket + ",";
    json += "\"symbol\":\"" + JsonEscape(symbol) + "\",";
    json += "\"position_type\":\"" + PositionTypeToString(type) + "\",";
    json += "\"volume\":" + DoubleToString(volume, 2) + ",";
    json += "\"price_open\":" + DoubleToString(price_open, (int)SymbolInfoInteger(symbol, SYMBOL_DIGITS)) + ",";
    json += "\"sl\":" + DoubleToString(sl, (int)SymbolInfoInteger(symbol, SYMBOL_DIGITS)) + ",";
    json += "\"tp\":" + DoubleToString(tp, (int)SymbolInfoInteger(symbol, SYMBOL_DIGITS)) + ",";
    json += "\"profit\":" + DoubleToString(profit, 2) + ",";
    if (t_open > 0) json += "\"time_open\":\"" + ToIso8601(t_open) + "\"";
    else json += "\"time_open\":null";
    json += "}";
  }
  json += "],";

  json += "\"sent_at\":\"" + ToIso8601(0) + "\"";
  json += "}";
  return json;
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
  value = StringToDouble(num);
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
  int status;
  return HttpRequest("POST", InpServerUrl + "/api/v1/mt5/action-results", body, resp, status) && (status >= 200 && status < 300);
}

void ExecuteActions(const string mt5_login, const string mt5_server)
{
  string url = InpServerUrl + "/api/v1/mt5/actions?mt5_login=" + UrlEncode(mt5_login) + "&mt5_server=" + UrlEncode(mt5_server) + "&platform=mt5";

  string resp;
  int status;
  if (!HttpRequest("GET", url, "", resp, status) || status < 200 || status >= 300)
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
      if (PositionSelectByTicket((ulong)ticket))
      {
        string sym = PositionGetString(POSITION_SYMBOL);
        ok = trade.PositionClose(sym, volume);
        if (!ok)
        {
          err = (long)trade.ResultRetcode();
          err_msg = trade.ResultRetcodeDescription();
        }
      }
      else
      {
        ok = true;
      }
    }
    else if (action_type == "close" && target_kind == "order")
    {
      if (OrderSelect((ulong)ticket))
      {
        ok = trade.OrderDelete((ulong)ticket);
        if (!ok)
        {
          err = (long)trade.ResultRetcode();
          err_msg = trade.ResultRetcodeDescription();
        }
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

void SyncOnce(const string mt5_login, const string mt5_server)
{
  if (InpApiKey == "" || InpServerUrl == "")
    return;

  if (InpDebug)
  {
    Print(
      "SyncOnce mt5_login=", mt5_login,
      " mt5_server=", mt5_server,
      " url=", InpServerUrl
    );
  }

  string body = BuildSyncPayload(mt5_login, mt5_server);
  string resp;
  int status;
  string url = InpServerUrl + "/api/v1/mt5/sync?mt5_login=" + UrlEncode(mt5_login) + "&mt5_server=" + UrlEncode(mt5_server);
  bool ok = HttpRequest("POST", url, body, resp, status);
  if (!ok)
  {
    int le = GetLastError();
    if (le == 4014)
      Print("WebRequest 失败：URL 未被允许，请在 MT5 里 Tools -> Options -> Expert Advisors 添加 URL：", InpServerUrl);
    else
      Print("WebRequest 失败，LastError=", le);
    ResetLastError();
    return;
  }
  if (status < 200 || status >= 300)
    Print("同步失败，HTTP=", status, " resp=", resp);
}

int OnInit()
{
  Print("TraderW_Relay_MT5 version=", EA_VERSION, " serverUrl=", InpServerUrl);
  EventSetTimer(MathMax(10, InpIntervalSeconds));
  return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
  EventKillTimer();
}

void OnTimer()
{
  string mt5_login;
  string mt5_server;
  if (!GetMt5Identity(mt5_login, mt5_server))
  {
    if (InpDebug)
      Print("Identity not ready: mt5_login=", (string)AccountInfoInteger(ACCOUNT_LOGIN), " mt5_server=", AccountInfoString(ACCOUNT_SERVER));
    return;
  }

  ExecuteActions(mt5_login, mt5_server);
  Sleep(100);
  SyncOnce(mt5_login, mt5_server);
}
