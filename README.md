bbs项目


通过git上传文件
首先进入你的master文件夹下，右键打开“Git Bash Here” ，弹出命令窗口 ，输入如下语句进行上传

git init ：在此文件夹生成一个.git隐藏文件；
git add . : 将文件添加到缓存区( 注意这个"."，是有空格的，"."代表这个test这个文件夹下的目录全部都提交，也可以通过git add 文件名 提交指定的文件)；
git status：查看现在的状态，也可以不看，随你啦，可以看到picture文件夹里面的内容都提交上去了；
git commit -m "这里是注释"：提交添加到缓存区的文件
git remote add origin https://xxx@xxx/test.git ： 添加新的git方式的origin, github上创建好的仓库和本地仓库进行关联




更新仓库文件
如果对本地文件有了修改，则需要对仓库文件进行更新，比如本地文件中删除了一个文件。 下面将显示如何对仓库更新。

首先进入你的master文件夹下，右键打开“Git Bash Here” ，弹出命令窗口 ，输入如下内容

输入 以下文本即可更新仓库

git status

git add -A

git commit -a -m "update" ： 能提交修改过，但是没有添加到缓存区的文件（修改过的就能提交）

git push origin master -f