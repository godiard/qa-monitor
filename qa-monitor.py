import os
from subprocess import Popen, STDOUT, PIPE
import json

MAX_DEPTH = 200


def _exec_command(path, *args):
    """Run a git command in path and return the result. Throws on error."""
    if not path:
        path = '.'
    print list(args)
    proc = Popen(list(args), stdout=PIPE, stderr=PIPE, cwd=path)

    out, err = [x.decode('utf-8') for x in proc.communicate()]

    if proc.returncode:
        cmd = ' '.join(args)
        print "COMMAND"
        print cmd
        print "OUTPUT"
        print out
        raise Exception(
            "Error running %s:\n\tErr: %s\n\tOut: %s\n\tExit: %s"
            % (cmd, err, out, proc.returncode), exit_code=proc.returncode)
    return out


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
            _exec_command('.', 'git', 'clone', url)
        else:
            _exec_command(self.directory, 'git', 'pull')
        self.read_log()

    def read_log(self):
        # Read the log
        log_output = _exec_command(self.directory, 'git', 'log',
                                   '--pretty=format:%H|%aN|%s')
        self.log = []
        for line in log_output.split('\n'):
            # print line
            parts = line.split('|')
            commit_hash = parts[0]
            author = parts[1]
            subject = parts[2]
            commit = {'hash': commit_hash, 'author': author,
                      'subject': subject}
            self.log.append(commit)


class Testers:

    def __init__(self):
        # read testers and collectors
        # tester es findbugs, un script
        # collector es un script que devuelve un valor numerico
        print "Read processors and Collectors"
        self.data = json.load(open('./config.json'))
        self.processors = self.data['processors']
        print self.processors
        self.collectors = self.data['collectors']
        print self.collectors

    def execute_processors(self, directory, output):
        for processor in self.processors:
            out = _exec_command(directory, "../scripts/" + processor, output)
            print out

if __name__ == "__main__":
    repo = Repository('../superclubs')

    testers = Testers()
    output = "master.xml"
    print "Repo dir " + repo.directory
    testers.execute_processors(repo.directory, output)
