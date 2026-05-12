import { ChevronRight, FileWarning, LoaderCircle } from 'lucide-react'

import type { TaskDetail, TaskSummary } from '@/types'

type TaskTimelineProps = {
  tasks: TaskSummary[]
  taskDetail: TaskDetail | null
  onInspect: (taskId: string) => void
}

const statusLabel: Record<TaskSummary['status'], string> = {
  queued: '等待中',
  running: '执行中',
  completed: '已完成',
  failed: '失败',
}

export function TaskTimeline({ tasks, taskDetail, onInspect }: TaskTimelineProps) {
  return (
    <section className="grid gap-5 lg:grid-cols-[0.9fr_1.1fr]">
      <div className="rounded-[30px] border border-[var(--line)] bg-white p-6">
        <div className="mb-4">
          <p className="text-xs uppercase tracking-[0.26em] text-[var(--muted)]">任务状态</p>
          <h2 className="mt-2 font-serif text-3xl">下载时间线</h2>
        </div>

        <div className="space-y-3">
          {tasks.length ? (
            tasks.map((task) => (
              <button
                key={task.id}
                className={`w-full rounded-[22px] border px-4 py-4 text-left transition ${
                  taskDetail?.id === task.id
                    ? 'border-[var(--accent)] bg-[var(--paper)]'
                    : 'border-[var(--line)] hover:bg-[var(--paper)]'
                }`}
                onClick={() => onInspect(task.id)}
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="line-clamp-1 text-sm font-medium text-[var(--ink)]">{task.title}</p>
                    <p className="mt-1 text-xs uppercase tracking-[0.14em] text-[var(--muted)]">
                      {statusLabel[task.status]}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-[var(--muted)]">
                    {task.status === 'running' ? <LoaderCircle className="animate-spin" size={14} /> : null}
                    {task.progress}%
                    <ChevronRight size={14} />
                  </div>
                </div>
              </button>
            ))
          ) : (
            <div className="rounded-[24px] border border-dashed border-[var(--line)] px-4 py-8 text-sm text-[var(--muted)]">
              还没有下载任务。解析成功后即可创建任务并在这里查看状态。
            </div>
          )}
        </div>
      </div>

      <div className="rounded-[30px] border border-[var(--line)] bg-[var(--card)] p-6">
        <div className="mb-4">
          <p className="text-xs uppercase tracking-[0.26em] text-[var(--muted)]">任务详情</p>
          <h2 className="mt-2 font-serif text-3xl">日志与文件结果</h2>
        </div>

        {taskDetail ? (
          <div className="space-y-5">
            <div className="rounded-[24px] bg-white px-5 py-5">
              <p className="text-lg font-medium text-[var(--ink)]">{taskDetail.title}</p>
              <p className="mt-1 text-sm text-[var(--muted)]">{taskDetail.url}</p>
              {taskDetail.error ? (
                <div className="mt-4 flex items-start gap-2 rounded-2xl bg-[var(--danger-bg)] px-4 py-3 text-sm text-[var(--danger-text)]">
                  <FileWarning size={16} />
                  {taskDetail.error}
                </div>
              ) : null}
            </div>

            <div className="rounded-[24px] bg-white px-5 py-5">
              <p className="mb-3 text-xs uppercase tracking-[0.18em] text-[var(--muted)]">输出文件</p>
              <div className="space-y-2 text-sm text-[var(--muted)]">
                {taskDetail.output_files.length ? (
                  taskDetail.output_files.map((filePath) => (
                    <p key={filePath} className="rounded-xl bg-[var(--paper)] px-3 py-2">
                      {filePath}
                    </p>
                  ))
                ) : (
                  <p>任务尚未完成，输出文件会在这里显示。</p>
                )}
              </div>
            </div>

            <div className="rounded-[24px] bg-white px-5 py-5">
              <p className="mb-3 text-xs uppercase tracking-[0.18em] text-[var(--muted)]">执行日志</p>
              <div className="max-h-72 space-y-2 overflow-auto pr-2 text-sm text-[var(--muted)]">
                {taskDetail.logs.length ? (
                  taskDetail.logs.map((line, index) => (
                    <p key={`${line}-${index}`} className="rounded-xl bg-[var(--paper)] px-3 py-2">
                      {line}
                    </p>
                  ))
                ) : (
                  <p>暂无日志。</p>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className="rounded-[24px] border border-dashed border-[var(--line)] px-4 py-8 text-sm text-[var(--muted)]">
            选择左侧任务后，这里会展示日志、文件输出和失败原因。
          </div>
        )}
      </div>
    </section>
  )
}
