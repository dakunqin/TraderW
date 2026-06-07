import type { ReactNode } from 'react'

import { cn } from '@/lib/utils'

export default function PageHeader(props: { title: string; subtitle?: string; right?: ReactNode }) {
  return (
    <div className="mb-6 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
      <div>
        <div className="text-lg font-semibold tracking-wide">{props.title}</div>
        {props.subtitle ? <div className={cn('mt-1 text-sm text-zinc-400')}>{props.subtitle}</div> : null}
      </div>
      {props.right ? <div className="flex items-center gap-2">{props.right}</div> : null}
    </div>
  )
}
