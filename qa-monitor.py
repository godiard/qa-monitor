import os
from subprocess import Popen, STDOUT, PIPE

MAX_DEPTH = 200


class Repository:

    def __init__(self, url):
        """Create a Repo object from the repository at url"""
        # url = git@gitlab.trinom.io:beagle/superclubs.git
        # url = git@github.com:godiard/typing-turtle-activity.git
        self.url = url

        self.directory = self.url[self.url.rfind('/')+1:]
        if '.git'in self.directory:
            self.directory = self.directory[:self.directory.rfind('.git')]

        print 'Directory ' + self.directory
        if not os.path.exists(self.directory):
            self._exec_command('.', 'clone', url)
        self.read_log()

    def read_log(self):
        # Read the log
        log_output = self._exec_command(self.directory, 'log',
                                        '--pretty=format:%H|%aN|%s')
        self.log = []
        for line in log_output.split('\n'):
            print line
            parts = line.split('|')
            commit_hash = parts[0]
            author = parts[1]
            subject = parts[2]
            commit = {'hash': commit_hash, 'author': author,
                      'subject': subject}
            self.log.append(commit)

    def _exec_command(self, path, *args):
        """Run a git command in path and return the result. Throws on error."""
        if not path:
            path = '.'
        proc = Popen(["git"] + list(args), stdout=PIPE, stderr=PIPE, cwd=path)

        out, err = [x.decode('utf-8') for x in proc.communicate()]

        if proc.returncode:
            cmd = 'git ' + ' '.join(args)
            raise Exception(
                "Error running %s:\n\tErr: %s\n\tOut: %s\n\tExit: %s"
                % (cmd, err, out, proc.returncode), exit_code=proc.returncode)
        return out


if __name__ == "__main__":
    repo = Repository('../superclubs')
