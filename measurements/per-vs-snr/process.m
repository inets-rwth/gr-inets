dirs = readdir('.');
for dir = dirs'
  if !strcmp(dir,'.') && !strcmp(dir,'..')
    files = readdir(dir)
    if(length(files) == 3)
      file = files(3)
    end
  end
end