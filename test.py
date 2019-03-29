import git

git_dir = "testdotfiles"
g = git.cmd.Git(git_dir)

g.pull()
