import io
import sys
from wavesynlib.languagecenter.wspp.process import preprocess



if __name__ == "__main__":
    source = sys.argv[1]
    with open(source, 'r') as sourcef:
        codestr = sourcef.read()
    newcode = "\n".join(preprocess(iter(codestr.split("\n"))))
    ########################################################################
    with open("d:/lab/wspp/tempcode.txt", "w") as f: 
        f.write(newcode)
    ##########################################
    target = sys.argv[2]
    try:
        if target == "-":
            targetf = sys.stdout
        else:
            targetf = open(target, 'w')
        tempout = io.StringIO()
        sout_backup = sys.stdout
        sys.stdout = tempout
        exec(newcode)
        gencode = tempout.getvalue()
        print(gencode, file=targetf)
    finally:
        sys.stdout = sout_backup
        if target != "-":
            # target is not stdout
            targetf.close()