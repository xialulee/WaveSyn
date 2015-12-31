function [tree, var] = getMuPadExprTree(expr)
tree = evalin(symengine, sprintf('prog::exprlist(%s)', char(expr)));
tree = evalc('disp(tree)');
var  = evalc('disp(symvar(expr))');
end