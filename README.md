# FlowSage-Hack
FlowSage 是一款面向 CTF 与流量取证场景的桌面分析工具，技术栈是Go + Wails + VMProtect 的程序逆向，
本项目为练习型逆向项目，实现了 FlowSage 所有功能解锁，实测v4.0.0。

## 有哪些保护
die 竟然分析不出来 VMProtect 的版本：

```text
(Heur) Protection: Generic [Strange sections]
(Heur) Packer: Generic [Section #7 (".U\m") compressed + Section #0 (".text") has wrong offset and size + High entropy]
```

不过手动分析，能看出 VMProtect 3.x 的典型特征，采用的保护手段包括：

- **代码压缩与加密**  
- **入口点替换（Entry Point Obfuscation）**  
- **Import Table 隐藏/重建**  
- **动态 API 解析**  
- **反调试（Anti-Debugging）**  
- **完整性检查（Integrity Check）**  
- **自校验 / Anti-Patch**  
- **反修改（Anti-Tamper）**  
- **反 Hook（Anti-Hook）**  
- **运行时内存保护**  
- **关键 API 拦截/监控**  
- **内存保护动态修改**  
- **PE 结构重构**  

## 逆向思路

- dump 完整内存快照。
- 判定保护覆盖面。
- 定位 pclntab 并反查 moduledata 恢复符号；将内存镜像转换为 IDA 可加载的 PE 文件；通过全局指针回查重建被摧毁的导入表。
- 字符串 xref 关键函数，静态分析

## 免责声明

本项目 **仅用于学习与研究目的**。  
因使用本程序造成的任何后果，作者概不负责。

---

## 开源协议

本项目基于 MIT License
开源，可自由用于个人或商业用途，但需保留版权声明。
