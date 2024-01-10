#!/usr/bin/env python3
# coding=utf-8
import argparse
import getopt
import sys
import re

url_param_patterns = []

static_types = ("bmp", "bz2", "css", "doc", "eot", "flv", "gif", "gz", "ico", "jpeg", "jpg", "js", "less", "mp3", "mp4"
                "pdf","png", "rar", "rtf", "swf", "tar", "tgz", "txt", "wav", "woff", "xml", "zip")

parser = argparse.ArgumentParser(description='burplogfilter', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('--file', '-f', help='输入的文件路径', required=True)
parser.add_argument('--output', '-o', help='输出的文件路径', required=False)
parser.add_argument('--target', '-t', help='待保留的目标地址（正则）', required=False)
parser.add_argument('--debug', '-d', help='是否显示调试日期', required=False, default=False)
args = parser.parse_args()

DEBUG = args.debug

def main():
    global DEBUG

    filename = args.file
    target = args.target

    blocks = scrapBlocks(filename)
    filteredBlocks = []
    for block in blocks:
        if isBlockUseful(block, target):
            filteredBlocks.append(block)

    for block in filteredBlocks:
        outputBlock(block)


def scrapBlocks(filename):
    global DEBUG

    if DEBUG:
        print("Try to anayze file %s" % filename)

    with open(filename, 'rb') as f:
        content = f.read().decode('utf-8')
        blocks = re.findall(r'======================================================'
                            r'.*?======================================================'
                            r'.*?======================================================', content, re.S)
        if DEBUG:
            print("The file contains %s block(s)" % len(blocks))

    return blocks


def isBlockUseful(block, target, isFilterStaticResource=True):
    global url_param_patterns

    previous_line = ""
    for line in block.split("\n"):
        # 首先过滤静态资源
        if isFilterStaticResource and re.match("^GET", line) and line.split(" ")[1].split("?")[0].split(".")[-1] in static_types:
            if DEBUG:
                print("[DEBUG] Filter this static resource url %s" % line.split(" ")[1])
            return False
        # 然后过滤地址
        if target:
            m = re.match(r"^Host:(.*)", line)
            if m:
                full_url = m.group(1).strip() + previous_line.split(" ")[1]
                if re.match(target, full_url) and full_url not in url_param_patterns:
                    url_param_patterns.append(full_url)
                    return True
                elif DEBUG:
                    print("[DEBUG] Filter this host %s" % m.group(1).strip())
            previous_line = line
    return False


def generatePattern(method, url, params):
    pattern = []
    pattern.append(method)
    pattern.append(url)
    paramKeys = []
    for item in params.split("&"):
        paramKeys.append(item.split("=")[0])
    paramKeys.sort()
    pattern.extend(paramKeys)
    return pattern


def outputBlock(block):
    output_file = args.output
    if output_file:
        with open(output_file, "w") as outputFile:
            outputFile.write(block)
            print("结果输出到文件: {}".format(output_file))
    else:
        print("\n" + block + "\n\n\n\n")


if __name__ == '__main__':
    main()
