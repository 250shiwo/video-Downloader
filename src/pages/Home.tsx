import { useEffect } from 'react'

import { AppShell } from '@/components/AppShell'
import { DownloadPanel } from '@/components/DownloadPanel'
import { HeroPanel } from '@/components/HeroPanel'
import { MetadataCard } from '@/components/MetadataCard'
import { SummaryCard } from '@/components/SummaryCard'
import { SupportStrip } from '@/components/SupportStrip'
import { TaskTimeline } from '@/components/TaskTimeline'
import { useAppStore } from '@/store/useAppStore'

export default function Home() {
  const {
    busy,
    downloadItems,
    error,
    metadata,
    summary,
    taskDetail,
    tasks,
    url,
    clearMessage,
    inspectTask,
    loadSettings,
    loadTasks,
    parseUrl,
    setDownloadItem,
    setUrl,
    startDownload,
    summarizeTask,
  } = useAppStore()

  useEffect(() => {
    loadSettings().catch(() => undefined)
    loadTasks().catch(() => undefined)
  }, [loadSettings, loadTasks])

  useEffect(() => {
    const timer = window.setInterval(() => {
      loadTasks().catch(() => undefined)
      if (taskDetail?.id) {
        inspectTask(taskDetail.id).catch(() => undefined)
      }
    }, 4000)

    return () => window.clearInterval(timer)
  }, [inspectTask, loadTasks, taskDetail?.id])

  useEffect(() => {
    if (!error) return
    const timer = window.setTimeout(() => clearMessage(), 5000)
    return () => window.clearTimeout(timer)
  }, [clearMessage, error])

  return (
    <AppShell>
      <div className="space-y-8">
        <HeroPanel
          busy={busy}
          error={error}
          url={url}
          onDownload={() => startDownload().catch(() => undefined)}
          onParse={() => parseUrl().catch(() => undefined)}
          onUrlChange={setUrl}
        />

        <SupportStrip />

        <div className="grid gap-8 xl:grid-cols-[1.05fr_0.95fr]">
          <MetadataCard metadata={metadata} />
          <DownloadPanel
            busy={busy}
            items={downloadItems}
            onStart={() => startDownload().catch(() => undefined)}
            onToggle={setDownloadItem}
          />
        </div>

        <SummaryCard
          busy={busy}
          summary={summary}
          taskDetail={taskDetail}
          onSummarize={(taskId) => summarizeTask(taskId).catch(() => undefined)}
        />

        <TaskTimeline
          taskDetail={taskDetail}
          tasks={tasks}
          onInspect={(taskId) => inspectTask(taskId).catch(() => undefined)}
        />
      </div>
    </AppShell>
  )
}
