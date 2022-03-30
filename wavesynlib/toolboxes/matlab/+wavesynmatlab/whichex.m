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

    for idx = 1 : numel(s)
        line = s{idx};
        
        pattern = java.util.regex.Pattern.compile('^built-in \((.*)\)');
        matcher = pattern.matcher(java.lang.String(line));
        success = matcher.matches();

        if success
            fprintf('%s\n', line)
        else
            path = line;
            if exist(path)
                fprintf('%s\n', link_sel(path));
            else
                fprintf('%s\n', line);
            end
        end
        
    end
end


function [path, file] = pathsplit(path)
    [path, name, ext] = fileparts(path);
    file = [name, ext];
end


function result = link_sel(path)
    [folder, file] = pathsplit(path);
    result = strcat( ...
        sprintf('<a href="matlab:system(''explorer /select,%s'');">%s</a>\\', path, folder), ...
        sprintf('<a href="matlab:open(''%s'');">%s</a>', path, file));
end


function result = link_nosel(path)
    [folder, file] = pathsplit(path);
    result = strcat( ...
        sprintf('<a href="matlab:system(''explorer %s'');">%s</a>\\', folder, folder), ...
        file);
end
