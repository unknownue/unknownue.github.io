+++
title = "增强的Diff文件查看器"
date = "2023-06-01T15:30:00"
description = "展示增强型差异文件对比工具"
+++

# 增强的Diff文件查看器

本文演示了如何使用增强型差异文件对比工具来可视化代码变更。

## 基本示例

下面是一个简单的单文件差异示例：

<div id="basic-diff" class="diff-container"></div>
<div class="diff-view-controls">
  <button id="basic-diff-split" class="active">并排视图</button>
  <button id="basic-diff-unified">统一视图</button>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    var diffStr = `diff --git a/src/utils.rs b/src/utils.rs
index 1234567..abcdefg 100644
--- a/src/utils.rs
+++ b/src/utils.rs
@@ -1,8 +1,12 @@
 /// 计算两个数的和
 pub fn add(a: i32, b: i32) -> i32 {
+    // 添加调试日志
+    println!("计算: {} + {}", a, b);
     a + b
 }
 
-/// 计算两个数的差
+/// 计算两个数的差，确保结果不为负数
 pub fn subtract(a: i32, b: i32) -> i32 {
-    a - b
+    // 安全处理可能的溢出
+    a.checked_sub(b).unwrap_or(0)
 }`;

    // 初始化diff查看器
    var basicDiffUI = new Diff2HtmlUI(
        document.getElementById("basic-diff"),
        diffStr,
        {
            drawFileList: true,
            matching: 'lines',
            outputFormat: 'side-by-side',
            highlight: false
        }
    );
    basicDiffUI.draw();
    
    // 应用自定义语法高亮
    setTimeout(function() {
        applyHighlighting('basic-diff');
    }, 100);
    
    // 设置视图控制按钮
    document.getElementById('basic-diff-split').addEventListener('click', function() {
        this.classList.add('active');
        document.getElementById('basic-diff-unified').classList.remove('active');
        basicDiffUI.draw('side-by-side');
        setTimeout(function() {
            applyHighlighting('basic-diff');
        }, 100);
    });
    
    document.getElementById('basic-diff-unified').addEventListener('click', function() {
        this.classList.add('active');
        document.getElementById('basic-diff-split').classList.remove('active');
        basicDiffUI.draw('line-by-line');
        setTimeout(function() {
            applyHighlighting('basic-diff');
        }, 100);
    });
    
    // 通用的语法高亮函数
    function applyHighlighting(containerId) {
        var codeContainers = document.querySelectorAll('#' + containerId + ' .d2h-code-line-ctn');
        
        codeContainers.forEach(function(container) {
            var html = container.innerHTML;
            
            // 跳过已高亮的内容
            if (html.includes('class="keyword"') || html.includes('class="comment"')) {
                return;
            }
            
            // 检测当前文件类型
            var fileElem = container.closest('.d2h-file-wrapper');
            var fileName = fileElem ? fileElem.querySelector('.d2h-file-name').textContent.trim() : '';
            var fileExt = fileName.split('.').pop().toLowerCase();
            
            if (fileExt === 'rs' || fileExt === 'rust') {
                // Rust语法高亮
                html = html.replace(/\b(fn|let|use|pub|struct|enum|impl|mut|if|else|return|match|for|while|loop|continue|break)\b/g, 
                    '<span class="keyword">$1</span>');
                
                // 注释
                html = html.replace(/(\/\/.*?$|\/\/!.*?$)/g, '<span class="comment">$1</span>');
                
                // 字符串
                html = html.replace(/"([^"\\]*(\\.[^"\\]*)*)"/g, '<span class="string">"$1"</span>');
                
                // 数字
                html = html.replace(/\b(\d+(\.\d+)?)\b/g, '<span class="number">$1</span>');
                
                // 函数名称
                html = html.replace(/\bfn\s+([a-zA-Z0-9_]+)/g, 'fn <span class="function">$1</span>');
            }
            
            // 更新HTML
            container.innerHTML = html;
        });
    }
});
</script>

## 多文件对比示例

下面是一个多文件差异对比示例：

<div id="multi-file-diff" class="diff-container"></div>
<div class="diff-view-controls">
  <button id="multi-file-diff-split" class="active">并排视图</button>
  <button id="multi-file-diff-unified">统一视图</button>
  <button id="multi-file-diff-toggle-files">文件列表</button>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    var multiFileDiffStr = `diff --git a/src/lib.rs b/src/lib.rs
index abcd123..efgh456 100644
--- a/src/lib.rs
+++ b/src/lib.rs
@@ -1,15 +1,20 @@
 //! 项目核心库
 
-/// 计算两个数的和
-pub fn add(a: i32, b: i32) -> i32 {
-    a + b
+/// 计算两个数的和并返回结果
+/// 
+/// # 参数
+/// * a - 第一个加数
+/// * b - 第二个加数
+pub fn add(a: i32, b: i32) -> i32 {
+    // 打印调试信息
+    println!("计算: {} + {}", a, b);
+    a + b
 }
 
 /// 计算两个数的差
 pub fn subtract(a: i32, b: i32) -> i32 {
-    a - b
+    a.checked_sub(b).unwrap_or(0)
 }
 
-/// 计算两个数的积
-pub fn multiply(a: i32, b: i32) -> i32 {
-    a * b
+/// 乘以一个数
+pub fn double(a: i32) -> i32 {
+    a * 2
 }
diff --git a/src/main.rs b/src/main.rs
index 123456..789abc 100644
--- a/src/main.rs
+++ b/src/main.rs
@@ -1,5 +1,10 @@
+use mylib::{add, double};
+
 fn main() {
-    println!("Hello, World!");
+    println!("Hello, Rust!");
+    
+    let result = add(5, 3);
+    println!("5 + 3 = {}", result);
+    
+    println!("Double of 10 is {}", double(10));
 }
-
-// 未使用的函数
diff --git a/Cargo.toml b/Cargo.toml
index 111222..333444 100644
--- a/Cargo.toml
+++ b/Cargo.toml
@@ -1,7 +1,12 @@
 [package]
-name = "example"
-version = "0.1.0"
+name = "mylib"
+version = "0.2.0"
 authors = ["Example Author <author@example.com>"]
 edition = "2021"
+description = "An example library with basic math functions"
+license = "MIT"
 
 [dependencies]
+log = "0.4"
+serde = { version = "1.0", features = ["derive"] }
+thiserror = "1.0"
`;

    // 初始化多文件diff查看器
    var multiFileDiffUI = new Diff2HtmlUI(
        document.getElementById("multi-file-diff"),
        multiFileDiffStr,
        {
            drawFileList: true,
            matching: 'lines',
            outputFormat: 'side-by-side',
            highlight: false
        }
    );
    multiFileDiffUI.draw();
    
    // 应用自定义语法高亮
    setTimeout(function() {
        applyMultiFileHighlighting('multi-file-diff');
    }, 100);
    
    // 设置视图控制按钮
    document.getElementById('multi-file-diff-split').addEventListener('click', function() {
        this.classList.add('active');
        document.getElementById('multi-file-diff-unified').classList.remove('active');
        multiFileDiffUI.draw('side-by-side');
        setTimeout(function() {
            applyMultiFileHighlighting('multi-file-diff');
        }, 100);
    });
    
    document.getElementById('multi-file-diff-unified').addEventListener('click', function() {
        this.classList.add('active');
        document.getElementById('multi-file-diff-split').classList.remove('active');
        multiFileDiffUI.draw('line-by-line');
        setTimeout(function() {
            applyMultiFileHighlighting('multi-file-diff');
        }, 100);
    });
    
    document.getElementById('multi-file-diff-toggle-files').addEventListener('click', function() {
        var fileList = document.querySelector('#multi-file-diff .d2h-file-list-wrapper');
        if (fileList) {
            fileList.style.display = fileList.style.display === 'none' ? 'block' : 'none';
        }
    });
    
    // 多文件语法高亮
    function applyMultiFileHighlighting(containerId) {
        var codeContainers = document.querySelectorAll('#' + containerId + ' .d2h-code-line-ctn');
        
        codeContainers.forEach(function(container) {
            var html = container.innerHTML;
            
            // 跳过已高亮的内容
            if (html.includes('class="keyword"') || html.includes('class="comment"')) {
                return;
            }
            
            // 检测当前文件类型
            var fileElem = container.closest('.d2h-file-wrapper');
            var fileName = fileElem ? fileElem.querySelector('.d2h-file-name').textContent.trim() : '';
            var fileExt = fileName.split('.').pop().toLowerCase();
            
            if (fileExt === 'rs') {
                // Rust语法高亮
                html = html.replace(/\b(fn|let|use|pub|struct|enum|impl|mut|if|else|return|match|for|while|loop|continue|break)\b/g, 
                    '<span class="keyword">$1</span>');
                
                // 注释
                html = html.replace(/(\/\/.*?$|\/\/!.*?$)/g, '<span class="comment">$1</span>');
                
                // 字符串
                html = html.replace(/"([^"\\]*(\\.[^"\\]*)*)"/g, '<span class="string">"$1"</span>');
                
                // 数字
                html = html.replace(/\b(\d+(\.\d+)?)\b/g, '<span class="number">$1</span>');
                
                // 函数名称
                html = html.replace(/\bfn\s+([a-zA-Z0-9_]+)/g, 'fn <span class="function">$1</span>');
                
                // 文档注释中的特殊标记
                html = html.replace(/(#\s*\w+)/g, '<span class="type">$1</span>');
            }
            else if (fileExt === 'toml') {
                // TOML语法高亮
                html = html.replace(/^(\s*[a-zA-Z0-9_.-]+)(\s*=)/gm, '<span class="function">$1</span>$2');
                
                // 节标题
                html = html.replace(/(\[.*?\])/g, '<span class="keyword">$1</span>');
                
                // 字符串
                html = html.replace(/(['"])(?:\\\1|.)*?\1/g, '<span class="string">$&</span>');
                
                // 数字
                html = html.replace(/\b(\d+(\.\d+)?)\b/g, '<span class="number">$1</span>');
            }
            
            // 更新HTML
            container.innerHTML = html;
        });
    }
});
</script>

## 使用短代码方式

除了直接在Markdown中使用内联代码，你也可以使用短代码来实现相同功能：

{% diff_viewer(
    id="shortcode-diff"
) %}
diff --git a/src/components/Button.jsx b/src/components/Button.jsx
index 1a2b3c4..5d6e7f8 100644
--- a/src/components/Button.jsx
+++ b/src/components/Button.jsx
@@ -1,13 +1,21 @@
-import React from 'react';
+import React, { useState } from 'react';
+import PropTypes from 'prop-types';
 
-const Button = ({ text, onClick }) => {
+const Button = ({ text, onClick, variant = 'primary', disabled = false }) => {
+  const [isHovered, setIsHovered] = useState(false);
+  
   return (
     <button 
-      className="button" 
+      className={`button button-${variant} ${isHovered ? 'hovered' : ''}`}
       onClick={onClick}
+      disabled={disabled}
+      onMouseEnter={() => setIsHovered(true)}
+      onMouseLeave={() => setIsHovered(false)}
     >
       {text}
     </button>
   );
 };
+
+Button.propTypes = {
+  text: PropTypes.string.isRequired,
+  onClick: PropTypes.func,
+  variant: PropTypes.oneOf(['primary', 'secondary', 'danger']),
+  disabled: PropTypes.bool
+};
{% end %}

## 特点与优势

这个增强的差异查看器包含以下特点：

1. **交互式UI**：用户可以在并排模式和统一模式之间切换
2. **文件导航**：对于多文件差异，可以通过文件列表快速跳转到特定文件
3. **智能语法高亮**：根据文件类型自动应用不同的语法高亮规则
4. **自适应主题**：支持浅色和深色模式
5. **可复用组件**：通过短代码或内联方式使用

## 视觉效果对比

增强的差异查看器带来了更直观、更专业的差异对比体验：

- 优化的颜色方案，可读性更高
- 更清晰的行高亮和内联差异标记
- 现代化的UI控件，交互体验更好
- 支持深色模式，保护眼睛

## 结论

通过使用这个增强的差异查看器，你可以在博客或文档中清晰地展示代码变更，提高读者的理解效率。无论是教程、变更日志还是代码分析，这个工具都能大幅提升内容的专业性和可读性。 