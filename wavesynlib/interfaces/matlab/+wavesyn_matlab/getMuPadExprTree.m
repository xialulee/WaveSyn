function tree = getMuPadExprTree(expr)
tree = evalin(symengine, sprintf('prog::exprlist(%s)', char(expr)));
tree = evalc('disp(tree)');
end