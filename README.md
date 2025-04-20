### 博客文章 https://blog.sfunction.top/posts/某课堂字体逆向以及自动答题/ 的完整代码实现

> [!TIP]
> 该代码只做学习交流以及复习使用

- 代码中所用cookie均已失效，若需复现，请自行更换data.json以及cookie (cookie中可能有些非必要的字段，当然目前这些字段是可以正常请求的)
  - 先更换data.json中的内容
  - 运行cor_mapping.py读取data.json中的font字段，以生成该次请求的正确映射表)
  - 运行analysis.py生成题库（建立在data.json是已全部答过的基础上）
- 若使用自动答题，更换data.json以及cookie即可正常使用
