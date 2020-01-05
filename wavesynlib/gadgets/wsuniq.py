import sys



def uniq(file, count=False):
    counter = 1
    buffer = file.readline()
    for line in file:
        if line == buffer:
            counter += 1
        else:
            if count:
                print(f'{counter}\t{buffer}')
            else:
                print(f'{buffer}')
            counter = 1
            buffer = line



def main():
    uniq(sys.stdin)



if __name__ == '__main__':
    main()
