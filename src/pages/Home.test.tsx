import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'

import Home from '@/pages/Home'

describe('Home page', () => {
  it('renders the main hero content', () => {
    render(
      <MemoryRouter>
        <Home />
      </MemoryRouter>,
    )

    expect(screen.getByText(/用一条链接，把多平台视频整理成可下载/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /解析视频/i })).toBeInTheDocument()
    expect(screen.getByText(/下载时间线/i)).toBeInTheDocument()
  })
})
