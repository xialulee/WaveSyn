function varargout = whichex(varargin)
    s = which(varargin{:});

    if nargout > 0
        varargout{1} = s;
        return;
    end

    if strcmp(s, '')
        fprintf(2, 'not found\n');
        return;
    end

    if ~iscell(s)
        s = {s};
    end

    open_folder = 'matlab:system(''explorer /select,%s'');';
    open_file = 'matlab:open(''%s'');';
    link = '<a href="%s">%s</a>\\<a href="%s">%s</a>';

    for idx = 1 : numel(s)
        pattern = java.util.regex.Pattern.compile('^built-in \((.*)\)');
        matcher = pattern.matcher(java.lang.String(s{idx}));
        success = matcher.matches();

        if success
            path = char(matcher.group(1));
            command = sprintf('built-in (%s)', link);
        else
            path = s{idx};
            command = link;
        end
        
        [folder, file] = pathsplit(path);    
        fprintf([command '\n'], ...
            sprintf(open_folder, path), ...
            folder, ...
            sprintf(open_file, path), ...
            file ...
        );    
    end
end


function [path, file] = pathsplit(path)
    [path, name, ext] = fileparts(path);
    file = [name, ext];
end