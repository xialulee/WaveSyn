function! CharDet()
py3 << EOF
import vim
from chardet.universaldetector import UniversalDetector
import codecs

detector = UniversalDetector()
coding = vim.options['encoding'].decode()
for line in vim.current.buffer:
  detector.feed(line.encode(coding))
  if detector.done:
    break
detector.close()
result = detector.result
print(result)
EOF
endfunction

