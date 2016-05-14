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
        print 'COMMAND'
        print cmd
        print 'OUTPUT'
        print out
        raise Exception(
            'Error running %s:\n\tErr: %s\n\tOut: %s\n\tExit: %s'
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
            _exec_command(self.directory, 'git', 'checkout', 'master')
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
            commit = {'commit_hash': commit_hash, 'author': author,
                      'subject': subject}
            self.log.append(commit)

    def run_tests(self, tester):
        for n in range(MAX_DEPTH):
            commit_hash = self.log[n]['commit_hash']
            print "Testing commit " + commit_hash
            _exec_command(self.directory, 'git', 'checkout', commit_hash)
            output_path = '../data/' + commit_hash + '.xml'
            if not os.path.exists(output_path):
                tester.execute_processors(self.directory, output_path)
            tester.execute_collectors(self.directory, commit_hash,
                                      output_path)


class Tester:

    def __init__(self):
        # read processors and collectors
        # tester es findbugs, un script
        # collector es un script que devuelve un valor numerico
        print 'Read processors and Collectors'
        self.data = json.load(open('./config.json'))
        self.processors = self.data['processors']
        print self.processors
        self.collectors = self.data['collectors']
        print self.collectors
        # verify if data and results directories exist
        if not os.path.exists('data'):
            os.mkdir('data')
        if not os.path.exists('results'):
            os.mkdir('results')

    def execute_processors(self, directory, output_path):
        for processor in self.processors:
            out = _exec_command(directory, '../scripts/' + processor,
                                output_path)
            print out

    def execute_collectors(self, directory, commit_hash, input_path):
        for collector in self.collectors:
            out = _exec_command(directory, '../scripts/' + collector['script'],
                                input_path)
            print 'collector ' + collector['id'] + ' = ' + out
            if 'results' not in collector:
                collector['results'] = []
            collector['results'].append({'commit_hash': commit_hash,
                                         'value': int(out)})


if __name__ == '__main__':
    repo = Repository('git@gitlab.trinom.io:beagle/superclubs.git')
    tester = Tester()
    repo.run_tests(tester)
