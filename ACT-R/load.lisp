(asdf:load-system 'actr6 :force t)
(load (concatenate 'string (directory-namestring (current-pathname)) "sf5-model-v1.lisp"))
(run-full-time 5 :real-time t)
