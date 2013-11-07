(asdf:load-system 'actr6 :force nil)
(load (concatenate 'string (directory-namestring (current-pathname)) "sf5-model-v1.lisp"))
(run-full-time 10 :real-time t)
