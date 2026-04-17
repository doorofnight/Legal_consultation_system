/**
 * 打字机效果工具函数
 * 提供逐步显示文本的功能，支持Markdown实时渲染
 */

export interface TypewriterOptions {
  /** 打字速度（毫秒/字符），默认30ms */
  speed?: number
  /** 是否启用Markdown渲染，默认true */
  markdown?: boolean
  /** Markdown渲染器函数，如果不提供则使用纯文本 */
  markdownRenderer?: (text: string) => string
  /** 每次渲染后的回调 */
  onUpdate?: (displayText: string) => void
  /** 打字完成后的回调 */
  onComplete?: () => void
}

export class Typewriter {
  private buffer: string = ''
  private displayText: string = ''
  private intervalId: number | null = null
  private options: Required<TypewriterOptions>
  private isComplete: boolean = false

  constructor(options: TypewriterOptions = {}) {
    this.options = {
      speed: options.speed ?? 30,
      markdown: options.markdown ?? true,
      markdownRenderer: options.markdownRenderer ?? ((text: string) => text),
      onUpdate: options.onUpdate ?? (() => {}),
      onComplete: options.onComplete ?? (() => {})
    }
  }

  /**
   * 开始打字效果
   * @param text 要显示的文本
   */
  start(text: string): void {
    this.reset()
    this.buffer = text
    this.displayText = ''
    this.isComplete = false

    // 使用requestAnimationFrame优化初始渲染
    requestAnimationFrame(() => {
      this.intervalId = window.setInterval(() => {
        this.typeNextChar()
      }, this.options.speed)
    })
  }

  /**
   * 输入下一个字符
   */
  private typeNextChar(): void {
    if (this.buffer.length === 0) {
      this.complete()
      return
    }

    // 取出下一个字符
    const nextChar = this.buffer[0]
    this.buffer = this.buffer.slice(1)
    this.displayText += nextChar

    // 使用requestAnimationFrame优化渲染
    requestAnimationFrame(() => {
      let renderedText = this.displayText
      
      // 如果需要Markdown渲染
      if (this.options.markdown && this.options.markdownRenderer) {
        renderedText = this.options.markdownRenderer(this.displayText)
      }
      
      this.options.onUpdate(renderedText)
    })
  }

  /**
   * 立即完成显示所有文本
   */
  completeImmediately(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId)
      this.intervalId = null
    }

    this.displayText += this.buffer
    this.buffer = ''
    
    requestAnimationFrame(() => {
      let renderedText = this.displayText
      
      if (this.options.markdown && this.options.markdownRenderer) {
        renderedText = this.options.markdownRenderer(this.displayText)
      }
      
      this.options.onUpdate(renderedText)
      this.complete()
    })
  }

  /**
   * 完成打字
   */
  private complete(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId)
      this.intervalId = null
    }
    
    this.isComplete = true
    this.options.onComplete()
  }

  /**
   * 重置打字机状态
   */
  reset(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId)
      this.intervalId = null
    }
    
    this.buffer = ''
    this.displayText = ''
    this.isComplete = false
  }

  /**
   * 检查是否已完成
   */
  get completed(): boolean {
    return this.isComplete
  }

  /**
   * 获取当前显示的文本
   */
  get text(): string {
    return this.displayText
  }

  /**
   * 追加内容到缓冲区（用于流式更新）
   * @param newContent 要追加的新内容
   */
  updateContent(newContent: string): void {
    this.buffer += newContent
    
    // 如果打字机已经完成但有新内容，重新启动打字机效果
    if (this.isComplete && this.buffer.length > 0) {
      this.isComplete = false
      // 重新启动间隔
      if (this.intervalId === null) {
        this.intervalId = window.setInterval(() => {
          this.typeNextChar()
        }, this.options.speed)
      }
    }
  }

  /**
   * 销毁实例，清理资源
   */
  destroy(): void {
    this.reset()
  }
}

/**
 * 创建打字机效果的快捷函数
 */
export function createTypewriter(
  element: HTMLElement,
  text: string,
  options: TypewriterOptions = {}
): Typewriter {
  const typewriter = new Typewriter({
    ...options,
    onUpdate: (displayText: string) => {
      element.innerHTML = displayText
      options.onUpdate?.(displayText)
    }
  })
  
  typewriter.start(text)
  return typewriter
}

/**
 * 批量管理多个打字机实例
 */
export class TypewriterManager {
  private instances: Map<string, Typewriter> = new Map()

  /**
   * 为指定元素创建打字机效果
   */
  create(
    id: string,
    element: HTMLElement,
    text: string,
    options: TypewriterOptions = {}
  ): Typewriter {
    // 如果已存在相同ID的实例，先销毁
    this.destroy(id)

    const typewriter = createTypewriter(element, text, options)
    this.instances.set(id, typewriter)
    return typewriter
  }

  /**
   * 获取指定ID的打字机实例
   */
  get(id: string): Typewriter | undefined {
    return this.instances.get(id)
  }

  /**
   * 销毁指定ID的打字机实例
   */
  destroy(id: string): void {
    const instance = this.instances.get(id)
    if (instance) {
      instance.destroy()
      this.instances.delete(id)
    }
  }

  /**
   * 销毁所有打字机实例
   */
  destroyAll(): void {
    this.instances.forEach(instance => instance.destroy())
    this.instances.clear()
  }

  /**
   * 立即完成所有打字机效果
   */
  completeAll(): void {
    this.instances.forEach(instance => {
      if (!instance.completed) {
        instance.completeImmediately()
      }
    })
  }
}