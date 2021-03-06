'''
Dumps PubMed abstracts to a common text file format for bulk preprocessing

FORMAT:
~~_PMID_XXXXXX_~~
TEXT
..

'''

import os
import glob
import codecs
import argparse
import lxml.etree as et
from pubtator.parsers import PubTatorDocPreprocessor

def parse_xml_format(filename, outputdir):
    """
    NLM XML Format
    :param filename:
    :param outputdir:
    :return:
    """
    doc_xpath      = './/PubmedArticle'
    id_xpath       = './MedlineCitation/PMID/text()'
    title_xpath    = './MedlineCitation/Article/ArticleTitle/text()'
    abstract_xpath = './MedlineCitation/Article/Abstract/AbstractText/text()'

    errors = 0
    outfile = os.path.basename(filename)
    outfile = ".".join(outfile.split(".")[0:-1])
    outfile = "{}/{}.txt".format(outputdir.replace(os.path.basename(filename), ""), outfile)

    with codecs.open(outfile, "w", "utf-8") as op:
        for i, doc in enumerate(et.parse(filename).xpath(doc_xpath)):
            try:
                pmid = doc.xpath(id_xpath)[0]
                title = doc.xpath(title_xpath)[0] if doc.xpath(title_xpath) else ""
                abstract = doc.xpath(abstract_xpath)[0] if doc.xpath(abstract_xpath) else ""
                text = u"{} {}".format(title, abstract)
                op.write(u"~~_PMID_{}_~~\n".format(pmid))
                op.write(text + u"\n")
            except:
                errors += 1

    print "Wrote", outfile
    return errors

def parse_bioc_format(filename, outputdir):
    
    """
    BioC XML Format
    :param filename:
    :param outputdir:
    :return:
    """
    
    doc_xpath      = './/document'
    id_xpath       = './/id/text()'
    ab_text = './/passage/text/text()'

    errors = 0
    outfile = os.path.basename(filename)
    outfile = ".".join(outfile.split(".")[0:-1])
    outfile = "{}/{}.txt".format(outputdir.replace(os.path.basename(filename), ""), outfile)
    with codecs.open(outfile, "w", "utf-8") as op:
        for i, doc in enumerate(et.parse(filename).xpath(doc_xpath)):
            try:
                pmid = doc.xpath(id_xpath)[0]
                # abstract = doc.xpath(abstract_xpath)[0] if doc.xpath(abstract_xpath) else ""
                text = '\n'.join(
                    filter(lambda t: t is not None, doc.xpath(ab_text))
                )
                op.write(u"~~_PMID_{}_~~\n".format(pmid))
                op.write(text + u"\n")
            except:
                errors += 1

    print "Wrote", outfile
    return errors

def parse_standoff_format(filename, outputdir, prefix="tmp"):
    """

    :param filename:
    :param outputdir:
    :return:
    """
    pubtator = PubTatorDocPreprocessor("")

    errors = 0
    outfile = os.path.basename(filename)
    outfile = ".".join(outfile.split(".")[0:-1])
    outfile = "{}/{}.txt".format(outputdir.replace(os.path.basename(filename), ""), outfile)

    with codecs.open(outfile, "w", "utf-8") as op:
        for doc, text in pubtator.parse_file(filename, filename):
            op.write(u"~~_PMID_{}_~~\n".format(doc.name))
            op.write(text + u"\n")

    print "Wrote", outfile
    return errors

#Separate abstracts into document name and text for TSV
def parse_tsv(filename):
    with codecs.open(filename, encoding='utf-8') as tsv:
        for line in tsv:
            (doc_name, doc_text) = line.split('\t')
            yield doc_name,doc_text
def strip_special(s):
    return ''.join(c for c in s if ord(c) < 128)

def parse_tsv_format(filename, outputdir):
    """
    Parsing PubMed abstracts in TSV format
    :param filename:
    :param outputdir:
    :return:
    """
    
    errors = 0
    outfile = os.path.basename(filename)
    outfile = ".".join(outfile.split(".")[0:-1])
    outfile = "{}/{}.txt".format(outputdir.replace(os.path.basename(filename), ""), outfile)

    tsv = parse_tsv(filename)
    with codecs.open(outfile, "w", "utf-8") as op:
        for doc, text in tsv:
            try:
                op.write(u"~~_PMID_{}_~~\n".format(doc))
                op.write(strip_special(text).strip() + u"\n")
            except:
                errors += 1

    print "Wrote", outfile
    return errors
def get_doc_parser(format):
    """
    Support various utililities for extracting text data

    :param format:
    :return:
    """
    if format == "xml":
        return parse_xml_format
    elif format == "bioc":
        return parse_bioc_format
    elif format == "tsv":
        return parse_tsv_format
    else:
        return parse_standoff_format

def main(args):

    doc_parser = get_doc_parser(args.format)

    filelist = glob.glob("{}/*".format(args.inputdir)) if os.path.isdir(args.inputdir) else [args.inputdir]

    for fp in filelist:
        if not os.path.exists(args.outputdir):
            os.mkdir(args.outputdir)

        errors = doc_parser(fp, args.outputdir)
        if errors:
            print "Errors: {}".format(errors)


if __name__ == '__main__':

    argparser = argparse.ArgumentParser()
    argparser.add_argument("-i", "--inputdir", type=str, default="input directory or file")
    argparser.add_argument("-o", "--outputdir", type=str, default="outout directory")
    argparser.add_argument("-f", "--format", type=str, default="pubtator")
    argparser.add_argument("-p", "--prefix", type=str, default="fixes", help="prefix")
    args = argparser.parse_args()

    args.outputdir = args.outputdir + "/tmp/"

    main(args)
