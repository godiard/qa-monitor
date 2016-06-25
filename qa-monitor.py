import os
import sys
import shutil
from subprocess import Popen, STDOUT, PIPE
import json
import time

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

    def __init__(self, url, update):
        """Create a Repo object from the repository at url"""
        # url = git@gitlab.trinom.io:beagle/superclubs.git
        # url = git@github.com:godiard/typing-turtle-activity.git
        self.url = url
        self._update = update

        self.directory = self.url[self.url.rfind('/')+1:]
        if '.git'in self.directory:
            self.directory = self.directory[:self.directory.rfind('.git')]

        print 'Directory ' + self.directory
        if not os.path.exists(self.directory):
            _exec_command('.', 'git', 'clone', url)
        else:
            _exec_command(self.directory, 'git', 'checkout', 'master')
            if self._update:
                _exec_command(self.directory, 'git', 'pull')
        self.read_log()

    def read_log(self):
        # Read the log
        log_output = _exec_command(self.directory, 'git', 'log',
                                   '--pretty=format:%H|%aN|%s',
                                   '--simplify-merges')
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
        # verify if data and results directories exist
        data_directory = 'data_' + self.directory
        if not os.path.exists(data_directory):
            os.mkdir(data_directory)

        collectors_data_path = os.path.join(
            data_directory, 'collectors_data.json')

        results = {}
        if os.path.exists(collectors_data_path):
            results = json.load(open(collectors_data_path))

        # count how many new commits there are
        new_commits = 0
        for n in range(MAX_DEPTH):
            commit_hash = self.log[n]['commit_hash']
            output_path = './' + data_directory + '/' + commit_hash + '.xml'
            if not os.path.exists(output_path):
                new_commits = new_commits + 1
        print "NEW COMMITS: %d" % new_commits

        for n in range(MAX_DEPTH):
            commit_hash = self.log[n]['commit_hash']
            if commit_hash in results:
                tester.load_data(commit_hash, results[commit_hash])
            else:
                print "Testing commit " + commit_hash
                _exec_command(self.directory, 'git', 'checkout', commit_hash)
                output_path = '../%s/%s.xml' % (data_directory, commit_hash)
                # le quito un punto del principio porque el path es relativo a
                # ./scripts/
                if not os.path.exists(output_path.replace('..', '.')):
                    tester.execute_processors(self.directory, output_path)

                tester.execute_collectors(self.directory, commit_hash,
                                          output_path)

                results[commit_hash] = tester.save_data(commit_hash)

        json.dump(results, open(collectors_data_path, 'w'))

        # convert the last findbugs file to text
        out = _exec_command(
            '.', '../tools/findbugs-3.0.1/bin/convertXmlToText',
            './%s/%s.xml' % (data_directory, self.log[0]['commit_hash']))
        with open('%s/last_report.txt' % data_directory, 'w') as f:
            f.write(out)


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
        self.commits = []

    def execute_processors(self, directory, output_path):
        for processor in self.processors:
            out = _exec_command(directory, '../scripts/' + processor,
                                output_path, directory)
            print out

    def execute_collectors(self, directory, commit_hash, input_path):
        self.commits.append(commit_hash)
        for collector in self.collectors:
            out = _exec_command(directory, '../scripts/' + collector['script'],
                                input_path)
            print 'collector ' + collector['id'] + ' = ' + out
            if 'results' not in collector:
                collector['results'] = {}
            collector['results'][commit_hash] = [int(i) for i in out.split()]

    def load_data(self, commit_hash, results):
        self.commits.append(commit_hash)
        for collector in self.collectors:
            if 'results' not in collector:
                collector['results'] = {}
            collector['results'][commit_hash] = results[collector['id']]

    def save_data(self, commit_hash):
        results = {}
        for collector in self.collectors:
            results[collector['id']] = collector['results'][commit_hash]
        return results


class HtmlBuilder:

    def __init__(self, tester, project_name, gitlab_url):
        self.tester = tester
        self.project_name = project_name
        self.gitlab_url = gitlab_url
        self.create_page()
        self.copy_web_files()
        self.copy_findbugs_files()

    def create_page(self):
        # revert the commits order, we want show the last commits
        # at the right
        commits = list(reversed(self.tester.commits))

        head = """
        <html>
            <head>
            <link rel="stylesheet" type="text/css" href="./c3.css"/>
            <style>
                .title {
                    font-family: sans-serif;
                    padding: 30px 0 0 20px;
                }
                .chart {
                    width: 95%;
                    margin-left: 20px;
                    background-color: #eeeeee;
                }
            </style>
            <script type="text/javascript" src="./d3-3.5.6.min.js"></script>
            <script type="text/javascript" src="./c3.js"></script>
        """

        script = """<script>
                        function displayData(d, element) {
                            var commit_hash = commits[d.x];
                            var url = '%s/' + commit_hash;
                            var win = window.open(url, '_blank');
                            win.focus();
                        };

        """ % self.gitlab_url

        for collector in self.tester.collectors:
            # how many numeric values returns the collector
            values = 1
            if 'values' in collector:
                values = collector['values']

            if 'labels' not in collector:
                collector['labels'] = [collector['id']]

            collector_data = []
            collector_interesting_points = []
            for n in range(values):
                collector_data.append([])

            for n in range(values):
                collector_data[n].append(collector['labels'][n])

            for index, commit in enumerate(commits):
                for n in range(values):
                    try:
                        collector_data[n].append(
                            collector['results'][commit][n])
                        if index > 0:
                            prev_commit = commits[index - 1]
                            if collector['results'][commit][n] != \
                                    collector['results'][prev_commit][n]:
                                collector_interesting_points.append(index)
                    except:
                        print "Can't read value"

            for n in range(values):
                script += "var %s_%s = %s;\n" % (
                    collector['id'], n, json.dumps(collector_data[n]))
            script += "var %s_visible_points = %s;\n" % (
                collector['id'], json.dumps(collector_interesting_points))

            self.point_of_interest_report(collector, commits,
                                          collector_interesting_points)

        script += "var commits = " + json.dumps(commits) + ";\n"

        script += """
            function showCharts() {
        """
        for collector in self.tester.collectors:

            values = 1
            if 'values' in collector:
                values = collector['values']
            columns = ''
            for n in range(values):
                columns += collector['id'] + '_' + str(n) + ','
            columns = columns[:len(columns)-1]

            onclick_function = 'displayData'
            if 'script_poi' in collector:
                # the on click function is replaced to show the local page
                # to show the differences
                onclick_function = """

                        function (d, element) {
                            var commit_hash = commits[d.x];
                            var url = './%s-%s-' + commit_hash + '.html';
                            var win = window.open(url, '_blank');
                            win.focus();
                        }""" % (self.project_name, collector['id'])

            script += """
            var chart_%s = c3.generate({
                    data: {
                        columns: [%s],
                        onclick: %s,
                        color: function(color, d){
                            if (d.index == undefined) {
                                return color;
                            }
                            if (%s_visible_points.indexOf(d.index) >= 0) {
                                return "red"
                            }
                            return "transparent"
                        }

                    },
                    axis: {
                        x: {
                            type: 'category',
                            categories: commits,
                            show: false
                        },
                        y: {
                            tick: {
                                format: function (d) {
                                    return (parseInt(d) == d) ? d : null;
                                }
                            }
                         }
                    },
                    bindto: '#%s'
            });
            """ % (collector['id'], columns, onclick_function, collector['id'],
                   collector['id'])

        script += """
            };
        </script>
        """

        body = """
            </head>
            <body onload="showCharts()">
                """
        body += "<h1 class='title'>%s</h1>" % self.project_name
        body += "<div class='container'>"
        body += "<p><a target='_blank' " + \
            "href='./%s.xml'>Last Findbugs xml file</a></p>" % \
            self.project_name
        body += "<p><a target='_blank' " + \
            "href='./%s.txt'>Last Findbugs report txt file</a></p>" % \
            self.project_name
        body += "<p>Generated: %s</p>" % time.strftime('%d/%b/%Y %H:%M')

        for collector in self.tester.collectors:
            body += """
                <h2 class='title'>%s</h2>
                <div class='chart'>
                <div id='%s'></div>
                </div>
                """ % (collector['titulo'], collector['id'])

        body += """
                </div>
            </body>
        </html>"""

        output_path = os.path.join(self.tester.data['output_path'],
                                   '%s.html' % self.project_name)
        with open(output_path, 'w') as f:
            f.write(head)
            f.write(script)
            f.write(body)

    def copy_web_files(self):
        output_path = self.tester.data['output_path']
        for file_name in os.listdir('web'):
            shutil.copy(os.path.join('web', file_name),
                        output_path)

    def copy_findbugs_files(self):
        output_path = self.tester.data['output_path']
        findbugs_file = './data_%s/%s.xml' % (self.project_name,
                                              self.tester.commits[0])
        destination = '%s/%s.xml' % (output_path, self.project_name)
        shutil.copyfile(findbugs_file, destination)

        txt_report_file = './data_%s/last_report.txt' % (self.project_name)
        destination = '%s/%s.txt' % (output_path, self.project_name)
        shutil.copyfile(txt_report_file, destination)

    def point_of_interest_report(self, collector, commits, poi_array):
        # commits: the list of commits in the graph,
        # are sorted in reversed order
        # poi_array: list of int with order in commits array
        # of changes in the values

        # verify if the collector have a script configured
        script = None
        if 'script_poi' in collector:
            script = collector['script_poi']
        else:
            return
        for order in poi_array:
            new_commit = commits[order]
            output_path = os.path.join(
                self.tester.data['output_path'],
                '%s-%s-%s.html' % (self.project_name, collector['id'],
                                   new_commit))
            if os.path.exists(output_path):
                continue

            if order > 0:
                last_commit = commits[order - 1]
                print 'COMMITS %s %s' % (last_commit, new_commit)
                out = _exec_command(
                    self.project_name, '../scripts/' + script,
                    '../data_%s/%s.xml' % (self.project_name, last_commit),
                    '../data_%s/%s.xml' % (self.project_name, new_commit))

                html = """
                <html>
                    <body>
                    <h1>Commit <a href="%s">%s</a></h1>
                    <pre>%s</pre>
                    </body>
                </html>""" % (self.gitlab_url + '/' + new_commit,
                              new_commit, out)
                with open(output_path, 'w') as f:
                    f.write(html)


if __name__ == '__main__':

    update = True

    for arg in sys.argv:
        if arg in ['-n', '--no-pull']:
            update = False

    projects = json.load(open('./projects.json'))
    for project in projects:
        repo = Repository(project['repository'], update)
        tester = Tester()
        repo.run_tests(tester)
        html_builder = HtmlBuilder(tester, project['name'],
                                   project['gitlab_commit_url'])
