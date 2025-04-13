# github-org-backup-tool
一个备份github上组织中所有仓库的简单工具, 在你的组织上实体名单前, 抢救你的组织的所有代码

# 使用指南
这个工具需要使用Github的`Personal access token`和`SSH Key`.
`Personal access token`是必须的, [这个链接](https://github.com/settings/tokens/new?scopes=admin:public_key,repo&description=BackupTool) 会创建一个`Personal access token`,带有仓库的访问权限
和创建`SSH Key`的权限. 如果不赋予`SSH Key`的创建权限, 你需要使用自己本地的`SSH Key`.

## 使用容器
挂在本地工作的`SSH Key`到容器, 并把本地的`~/BackupTool`作为备份目录
```shell script
 docker run --rm -it -v ~/.ssh:/root/.ssh:ro -v ~/BackupTool:/root/BackupTool hooyao/github-backup-tool:latest \
  sh ./start.sh  \
  -t personal_access_token \
  # don't change /root/BackupTool, it's the mounting point inside docker
  -d /root/BackupTool \ 
  -o organization_name_1
```
使用临时的`SSH Key`,这需要`Personal access token`中带有创建`SSH Key`的权限, 并且你的组织没有诸如SSO之类的权限设置
```shell script
 docker run --rm -it -v ~/BackupTool:/root/BackupTool hooyao/github-backup-tool:latest \
  sh ./start.sh  \
  -t personal_access_token \
  # don't change /root/BackupTool, it's the mounting point inside docker
  -d /root/BackupTool \ 
  -o organization_name_1
```