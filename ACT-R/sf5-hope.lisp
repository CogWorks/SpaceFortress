(defmacro defp (&rest body)
  `(p-fct ',body))

(defmacro defp* (&rest body)
  `(p*-fct ',body))

(defun run-until-break (&key (real-time nil))
  (run-until-condition (lambda () nil) :real-time real-time))

(clear-all)

(define-model spacefortress)

(jni-register-event-hook :break (lambda () (schedule-break-after-all)))

(sgp :jni-hostname "localhost" :jni-port 5555 :jni-sync t)

(sgp :needs-mouse nil
     :v t
     :esc t
     :er t
     :ul t
     :ppm 1
     :mas 1
     :mp 1
     )

(chunk-type task goal subgoal)
(chunk-type iffletter letter)

(defp **start-game?
      ?goal> buffer empty
      ?visual-location> buffer empty
      ==>
      +visual-location> isa visual-location kind text
      )

(defp **start-game!
      ?goal> buffer empty
      =visual-location> isa visual-location kind text
      ?manual> state free
      ==>
      +goal> isa task goal "does-game-have-mines"
      +manual> isa press-key key "return"
      )

(defp **does-game-have-mines?
      =goal> isa task goal "does-game-have-mines"
      ?visual-location> buffer empty
      ?manual> state free
      ==>
      +visual-location> isa visual-location kind text color "yellow" value "The Type-2 mines for this session are:"
      )

(defp **does-game-have-mines??
      =goal> isa task goal "does-game-have-mines"
      =visual-location> isa visual-location kind text - color "yellow" - value "The Type-2 mines for this session are:"
      ?manual> state free
      ==>
      +visual-location> isa visual-location kind text color "yellow" value "The Type-2 mines for this session are:"
      )

(defp **does-game-have-mines!
      =goal> isa task goal "does-game-have-mines"
      =visual-location> isa visual-location kind text color "yellow" value "The Type-2 mines for this session are:"
      ?manual> state free
      ==>
      +goal> isa task goal "study-iff-letters"
      )

(defp **find-iff-letter?
      =goal> isa task goal "study-iff-letters"
      ?visual-location> buffer empty - state error
      ?visual> buffer empty
      ?imaginal> state free
      ?manual> state free
      ==>
      +visual-location> isa visual-location kind text color "white" :attended nil
      )

(defp **find-iff-letter!
      =goal> isa task goal "study-iff-letters"
      ?visual-location> buffer full
      =visual-location> isa visual-location kind text color "white"
      ?visual> buffer empty state free
      ?imaginal> state free
      ?manual> state free
      ==>
      =visual-location>
      +visual> isa move-attention screen-pos =visual-location
      )

(defp **attend-iff-letter
      =goal> isa task goal "study-iff-letters"
      =visual> isa text value =letter
      ?manual> state free
      ==>
      +imaginal> isa iffletter letter =letter
      -visual>
      -visual-location>
      )

(defp **done-finding-iff-letters
      =goal> isa task goal "study-iff-letters"
      ?visual-location> buffer empty state error
      ?visual> buffer empty
      ?imaginal> state free
      ?manual> state free
      ==>
      =goal> goal "play"
      +visual-location> isa visual-location kind text :attended nil
      +manual> isa press-key key "return"
      )

(defp **do-nothing
      =goal> isa task goal "play"
      ==>
      =goal>
      )

(defp **ship-thrust
      =goal> isa task goal "play"
      ?manual> state free
      ==>
      =goal>
      +manual> isa press-key key "w"
      )

(defp **ship-turn-left
      =goal> isa task goal "play"
      ?manual> state free
      ==>
      =goal>
      +manual> isa press-key key "a"
      )

(defp **ship-turn-right
      =goal> isa task goal "play"
      ?manual> state free
      ==>
      =goal>
      +manual> isa press-key key "d"
      )