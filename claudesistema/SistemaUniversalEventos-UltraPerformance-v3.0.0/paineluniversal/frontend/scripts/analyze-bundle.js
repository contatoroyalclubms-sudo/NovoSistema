/**
 * BUNDLE ANALYSIS SCRIPT
 * Sistema Universal de Gestão de Eventos - ULTRA PERFORMANCE
 * 
 * Advanced bundle analysis with:
 * - Bundle size analysis
 * - Chunk optimization recommendations
 * - Dependency analysis
 * - Performance recommendations
 */

import { execSync } from 'child_process'
import fs from 'fs/promises'
import path from 'path'
import { fileURLToPath } from 'url'
import { createRequire } from 'module'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const require = createRequire(import.meta.url)

// Configuration
const CONFIG = {
  buildDir: path.resolve(__dirname, '../dist'),
  packageJsonPath: path.resolve(__dirname, '../package.json'),
  outputFile: path.resolve(__dirname, '../bundle-analysis.json'),
  thresholds: {
    totalSizeKB: 500,
    chunkSizeKB: 250,
    unusedCodePercent: 20,
    duplicateCodePercent: 10
  }
}

class UltraBundleAnalyzer {
  constructor() {
    this.analysis = {
      timestamp: new Date().toISOString(),
      summary: {},
      chunks: [],
      dependencies: [],
      recommendations: [],
      performance: {}
    }
  }

  async analyze() {
    console.log('🔍 Starting Ultra Bundle Analysis...')
    
    try {
      // Build the project first
      await this.buildProject()
      
      // Analyze bundle files
      await this.analyzeBundleFiles()
      
      // Analyze dependencies
      await this.analyzeDependencies()
      
      // Generate recommendations
      this.generateRecommendations()
      
      // Calculate performance metrics
      this.calculatePerformanceMetrics()
      
      // Save analysis results
      await this.saveAnalysis()
      
      // Display results
      this.displayResults()
      
      console.log('✅ Bundle analysis completed!')
      
    } catch (error) {
      console.error('❌ Bundle analysis failed:', error)
      throw error
    }
  }

  async buildProject() {
    console.log('📦 Building project for analysis...')
    
    try {
      // Build with bundle analysis
      execSync('npm run build', { 
        stdio: 'pipe',
        cwd: path.resolve(__dirname, '..')
      })
      console.log('✅ Build completed')
    } catch (error) {
      throw new Error(`Build failed: ${error.message}`)
    }
  }

  async analyzeBundleFiles() {
    console.log('📊 Analyzing bundle files...')
    
    try {
      const files = await this.getBundleFiles()
      let totalSize = 0
      
      for (const file of files) {
        const stats = await fs.stat(file.path)
        const gzippedSize = await this.estimateGzipSize(file.path)
        
        const chunk = {
          name: file.name,
          path: file.relativePath,
          size: stats.size,
          sizeKB: Math.round(stats.size / 1024),
          gzippedSize,
          gzippedSizeKB: Math.round(gzippedSize / 1024),
          compressionRatio: ((stats.size - gzippedSize) / stats.size * 100).toFixed(1),
          type: this.getFileType(file.name)
        }
        
        this.analysis.chunks.push(chunk)
        totalSize += stats.size
      }
      
      this.analysis.summary = {
        totalChunks: this.analysis.chunks.length,
        totalSize,
        totalSizeKB: Math.round(totalSize / 1024),
        totalGzippedSize: this.analysis.chunks.reduce((sum, chunk) => sum + chunk.gzippedSize, 0),
        totalGzippedSizeKB: Math.round(
          this.analysis.chunks.reduce((sum, chunk) => sum + chunk.gzippedSize, 0) / 1024
        )
      }
      
      console.log(`📈 Found ${files.length} chunks, total size: ${this.analysis.summary.totalSizeKB}KB`)
      
    } catch (error) {
      throw new Error(`Bundle file analysis failed: ${error.message}`)
    }
  }

  async getBundleFiles() {
    const distPath = CONFIG.buildDir
    const files = []
    
    async function scanDirectory(dir, relativePath = '') {
      const entries = await fs.readdir(dir, { withFileTypes: true })
      
      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name)
        const relPath = path.join(relativePath, entry.name)
        
        if (entry.isDirectory()) {
          await scanDirectory(fullPath, relPath)
        } else if (entry.isFile() && this.isBundleFile(entry.name)) {
          files.push({
            name: entry.name,
            path: fullPath,
            relativePath: relPath
          })
        }
      }
    }
    
    await scanDirectory.call(this, distPath)
    return files
  }

  isBundleFile(filename) {
    const bundleExtensions = ['.js', '.css', '.woff2', '.woff', '.svg', '.png', '.jpg', '.jpeg']
    const ext = path.extname(filename).toLowerCase()
    return bundleExtensions.includes(ext)
  }

  getFileType(filename) {
    const ext = path.extname(filename).toLowerCase()
    
    if (['.js', '.mjs'].includes(ext)) return 'javascript'
    if (ext === '.css') return 'stylesheet'
    if (['.woff', '.woff2', '.ttf', '.eot'].includes(ext)) return 'font'
    if (['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'].includes(ext)) return 'image'
    return 'other'
  }

  async estimateGzipSize(filePath) {
    try {
      const content = await fs.readFile(filePath)
      // Simple estimation: assume 30% compression for JS/CSS, 10% for images
      const ext = path.extname(filePath).toLowerCase()
      
      if (['.js', '.css'].includes(ext)) {
        return Math.round(content.length * 0.7) // 30% compression
      } else if (['.png', '.jpg', '.jpeg', '.gif'].includes(ext)) {
        return Math.round(content.length * 0.9) // 10% compression
      } else {
        return Math.round(content.length * 0.8) // 20% compression
      }
    } catch (error) {
      return 0
    }
  }

  async analyzeDependencies() {
    console.log('📦 Analyzing dependencies...')
    
    try {
      const packageJson = JSON.parse(
        await fs.readFile(CONFIG.packageJsonPath, 'utf-8')
      )
      
      const dependencies = {
        ...packageJson.dependencies,
        ...packageJson.devDependencies
      }
      
      for (const [name, version] of Object.entries(dependencies)) {
        try {
          const pkgPath = path.resolve(__dirname, '../node_modules', name, 'package.json')
          const pkgJson = JSON.parse(await fs.readFile(pkgPath, 'utf-8'))
          
          this.analysis.dependencies.push({
            name,
            version,
            description: pkgJson.description || '',
            size: await this.estimatePackageSize(name),
            type: packageJson.dependencies?.[name] ? 'production' : 'development'
          })
        } catch (error) {
          // Package might not exist or be accessible
          this.analysis.dependencies.push({
            name,
            version,
            description: 'Unknown',
            size: 0,
            type: packageJson.dependencies?.[name] ? 'production' : 'development',
            error: 'Could not analyze'
          })
        }
      }
      
      console.log(`📊 Analyzed ${this.analysis.dependencies.length} dependencies`)
      
    } catch (error) {
      console.warn(`⚠️ Dependency analysis failed: ${error.message}`)
    }
  }

  async estimatePackageSize(packageName) {
    try {
      const pkgPath = path.resolve(__dirname, '../node_modules', packageName)
      
      async function calculateDirSize(dirPath) {
        let size = 0
        const entries = await fs.readdir(dirPath, { withFileTypes: true })
        
        for (const entry of entries) {
          const fullPath = path.join(dirPath, entry.name)
          
          if (entry.isDirectory()) {
            size += await calculateDirSize(fullPath)
          } else if (entry.isFile()) {
            const stats = await fs.stat(fullPath)
            size += stats.size
          }
        }
        
        return size
      }
      
      return await calculateDirSize(pkgPath)
    } catch (error) {
      return 0
    }
  }

  generateRecommendations() {
    console.log('💡 Generating optimization recommendations...')
    
    const recommendations = []
    
    // Check total bundle size
    if (this.analysis.summary.totalGzippedSizeKB > CONFIG.thresholds.totalSizeKB) {
      recommendations.push({
        type: 'critical',
        category: 'bundle-size',
        title: 'Bundle size exceeds recommended limit',
        description: `Total gzipped size is ${this.analysis.summary.totalGzippedSizeKB}KB (limit: ${CONFIG.thresholds.totalSizeKB}KB)`,
        impact: 'high',
        suggestions: [
          'Enable code splitting for route-based chunks',
          'Use dynamic imports for large components',
          'Remove unused dependencies',
          'Consider using a smaller UI library alternative'
        ]
      })
    }
    
    // Check individual chunk sizes
    const largeChunks = this.analysis.chunks.filter(
      chunk => chunk.gzippedSizeKB > CONFIG.thresholds.chunkSizeKB
    )
    
    if (largeChunks.length > 0) {
      recommendations.push({
        type: 'warning',
        category: 'chunk-optimization',
        title: `${largeChunks.length} chunks exceed recommended size`,
        description: `Chunks larger than ${CONFIG.thresholds.chunkSizeKB}KB: ${largeChunks.map(c => c.name).join(', ')}`,
        impact: 'medium',
        suggestions: [
          'Split large chunks using dynamic imports',
          'Move third-party libraries to separate vendor chunks',
          'Use tree shaking to remove unused code'
        ]
      })
    }
    
    // Check for potential optimizations
    const jsChunks = this.analysis.chunks.filter(chunk => chunk.type === 'javascript')
    const cssChunks = this.analysis.chunks.filter(chunk => chunk.type === 'stylesheet')
    
    if (jsChunks.length > 10) {
      recommendations.push({
        type: 'info',
        category: 'chunk-count',
        title: 'Many JavaScript chunks detected',
        description: `${jsChunks.length} JS chunks may impact HTTP/1.1 performance`,
        impact: 'low',
        suggestions: [
          'Consider combining smaller chunks',
          'Ensure HTTP/2 is enabled on your server',
          'Use chunk optimization in build configuration'
        ]
      })
    }
    
    // Check compression ratios
    const poorCompression = this.analysis.chunks.filter(
      chunk => parseFloat(chunk.compressionRatio) < 20
    )
    
    if (poorCompression.length > 0) {
      recommendations.push({
        type: 'info',
        category: 'compression',
        title: 'Some files have poor compression ratios',
        description: `${poorCompression.length} files compress less than 20%`,
        impact: 'low',
        suggestions: [
          'Ensure gzip/brotli compression is enabled',
          'Optimize images using modern formats (WebP, AVIF)',
          'Minimize and optimize CSS/JS files'
        ]
      })
    }
    
    // Dependency recommendations
    const largeDependencies = this.analysis.dependencies
      .filter(dep => dep.size > 1024 * 1024) // > 1MB
      .sort((a, b) => b.size - a.size)
      .slice(0, 5)
    
    if (largeDependencies.length > 0) {
      recommendations.push({
        type: 'info',
        category: 'dependencies',
        title: 'Large dependencies detected',
        description: `Top large dependencies: ${largeDependencies.map(d => d.name).join(', ')}`,
        impact: 'medium',
        suggestions: [
          'Consider lighter alternatives for large dependencies',
          'Use tree shaking to import only needed parts',
          'Load large libraries dynamically when needed'
        ]
      })
    }
    
    this.analysis.recommendations = recommendations
    console.log(`💡 Generated ${recommendations.length} recommendations`)
  }

  calculatePerformanceMetrics() {
    console.log('⚡ Calculating performance metrics...')
    
    const jsSize = this.analysis.chunks
      .filter(chunk => chunk.type === 'javascript')
      .reduce((sum, chunk) => sum + chunk.gzippedSize, 0)
    
    const cssSize = this.analysis.chunks
      .filter(chunk => chunk.type === 'stylesheet')
      .reduce((sum, chunk) => sum + chunk.gzippedSize, 0)
    
    // Estimate loading times for different connection speeds
    const connectionSpeeds = {
      '3G': 1.6 * 1024 * 1024, // 1.6 Mbps
      '4G': 10 * 1024 * 1024,  // 10 Mbps
      'WiFi': 50 * 1024 * 1024  // 50 Mbps
    }
    
    const loadingTimes = {}
    for (const [speed, bps] of Object.entries(connectionSpeeds)) {
      const seconds = this.analysis.summary.totalGzippedSize / (bps / 8)
      loadingTimes[speed] = {
        seconds: Math.round(seconds * 10) / 10,
        rating: seconds < 2 ? 'excellent' : seconds < 5 ? 'good' : seconds < 10 ? 'fair' : 'poor'
      }
    }
    
    this.analysis.performance = {
      javascriptSizeKB: Math.round(jsSize / 1024),
      stylesheetSizeKB: Math.round(cssSize / 1024),
      loadingTimes,
      coreWebVitalsEstimate: {
        LCP: loadingTimes['3G'].seconds < 2.5 ? 'good' : loadingTimes['3G'].seconds < 4 ? 'needs-improvement' : 'poor',
        FID: jsSize < 100 * 1024 ? 'good' : jsSize < 300 * 1024 ? 'needs-improvement' : 'poor',
        CLS: 'estimated-good' // Would need runtime analysis
      }
    }
  }

  async saveAnalysis() {
    console.log('💾 Saving analysis results...')
    
    await fs.writeFile(
      CONFIG.outputFile,
      JSON.stringify(this.analysis, null, 2),
      'utf-8'
    )
    
    console.log(`📄 Analysis saved to: ${CONFIG.outputFile}`)
  }

  displayResults() {
    console.log('\n📊 ULTRA BUNDLE ANALYSIS RESULTS')
    console.log('================================')
    
    // Summary
    console.log('\n📈 Summary:')
    console.log(`  Total Size: ${this.analysis.summary.totalSizeKB}KB (${this.analysis.summary.totalGzippedSizeKB}KB gzipped)`)
    console.log(`  Total Chunks: ${this.analysis.summary.totalChunks}`)
    console.log(`  JS Size: ${this.analysis.performance.javascriptSizeKB}KB gzipped`)
    console.log(`  CSS Size: ${this.analysis.performance.stylesheetSizeKB}KB gzipped`)
    
    // Performance
    console.log('\n⚡ Performance Estimates:')
    for (const [speed, timing] of Object.entries(this.analysis.performance.loadingTimes)) {
      const emoji = timing.rating === 'excellent' ? '🚀' : timing.rating === 'good' ? '✅' : timing.rating === 'fair' ? '⚠️' : '❌'
      console.log(`  ${speed}: ${timing.seconds}s ${emoji}`)
    }
    
    // Top chunks by size
    console.log('\n📦 Largest Chunks:')
    const sortedChunks = [...this.analysis.chunks]
      .sort((a, b) => b.gzippedSize - a.gzippedSize)
      .slice(0, 5)
    
    sortedChunks.forEach(chunk => {
      console.log(`  ${chunk.name}: ${chunk.gzippedSizeKB}KB (${chunk.compressionRatio}% compression)`)
    })
    
    // Recommendations
    if (this.analysis.recommendations.length > 0) {
      console.log('\n💡 Recommendations:')
      this.analysis.recommendations.forEach(rec => {
        const emoji = rec.type === 'critical' ? '🚨' : rec.type === 'warning' ? '⚠️' : 'ℹ️'
        console.log(`  ${emoji} ${rec.title}`)
        console.log(`    Impact: ${rec.impact} | ${rec.description}`)
      })
    }
    
    // Overall grade
    const grade = this.calculateOverallGrade()
    console.log(`\n🎯 Overall Performance Grade: ${grade.letter} (${grade.score}/100)`)
    console.log(`   ${grade.message}`)
  }

  calculateOverallGrade() {
    let score = 100
    
    // Deduct points for bundle size
    if (this.analysis.summary.totalGzippedSizeKB > CONFIG.thresholds.totalSizeKB) {
      const excess = this.analysis.summary.totalGzippedSizeKB - CONFIG.thresholds.totalSizeKB
      score -= Math.min(30, excess / 10) // Max 30 points deduction
    }
    
    // Deduct points for large chunks
    const largeChunks = this.analysis.chunks.filter(
      chunk => chunk.gzippedSizeKB > CONFIG.thresholds.chunkSizeKB
    )
    score -= Math.min(20, largeChunks.length * 5)
    
    // Deduct points for critical recommendations
    const criticalRecs = this.analysis.recommendations.filter(rec => rec.type === 'critical')
    score -= criticalRecs.length * 15
    
    // Deduct points for warning recommendations
    const warningRecs = this.analysis.recommendations.filter(rec => rec.type === 'warning')
    score -= warningRecs.length * 5
    
    score = Math.max(0, Math.round(score))
    
    let letter, message
    if (score >= 90) {
      letter = 'A'
      message = 'Excellent bundle optimization! 🚀'
    } else if (score >= 80) {
      letter = 'B'
      message = 'Good bundle performance with room for improvement ✅'
    } else if (score >= 70) {
      letter = 'C'
      message = 'Acceptable performance, consider optimizations ⚠️'
    } else if (score >= 60) {
      letter = 'D'
      message = 'Bundle needs optimization for better performance ❌'
    } else {
      letter = 'F'
      message = 'Critical performance issues need immediate attention 🚨'
    }
    
    return { score, letter, message }
  }
}

// Run analysis if this script is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const analyzer = new UltraBundleAnalyzer()
  
  analyzer.analyze().catch(error => {
    console.error('Analysis failed:', error)
    process.exit(1)
  })
}

export { UltraBundleAnalyzer }