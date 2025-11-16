# aur

此项目为 imlonghao 负责的 Arch User Repository (AUR) 仓库

## 常用流程

### 更新软件

1. 更新对应包目录中 `PKGBUILD` 的 `pkgver` 字段
2. 在该目录下运行 `makepkg -g` 获取最新的文件签名
3. 替换 `PKGBUILD` 中的文件签名
4. 运行 `git commit -am '软件包名: 0.0.0 -> 1.1.1'`，其中 `0.0.0` 为老版本号，`1.1.1` 为新版本号
5. 运行 `git push`
