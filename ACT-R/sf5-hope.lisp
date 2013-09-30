(defmacro defp (&rest body)
  `(p-fct ',body))

(defmacro defp* (&rest body)
  `(p*-fct ',body))

(defun run-until-break (&key (real-time nil))
  (run-until-condition (lambda () nil) :real-time real-time))

(defun degrees (x) (* x (/ 180 pi)))

(defun to-target-orientation(selfx selfy targx targy)
  (round (mod (- (degrees (atan (- targx selfx) (- selfy targy))) 90) 360)))

(defun point-on-line (px py x1 y1 x2 y2)
  (= (- py y1) (* (/ (- y2 y1) (- x2 x1)) (- px x1))))

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
     :randomize-time nil
     )

;;; Goals
(chunk-type monitor)
(chunk-type shoot-fortress subgoal)
(chunk-type shoot-mine subgoal)
(chunk-type avoid-shells subgoal)
(chunk-type avoid-fortress subgoal)
(chunk-type avoid-warping subgoal)
(chunk-type avoid-mine subgoal)

;;; New chunk types
(chunk-type (token-location (:include visual-location)) orientation velocity)
(chunk-type (token-object (:include visual-object)) orientation velocity)
(chunk-type (ship (:include token-object)))
(chunk-type (fortress (:include token-object)))
(chunk-type (mine (:include token-object)))
(chunk-type (shell (:include token-object)))
(chunk-type (missile (:include token-object)))

;;; Old chunk types
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
  +manual> isa delayed-punch hand right finger pinky
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
  +goal> isa monitor
  +visual-location> isa visual-location kind text :attended nil
  +manual> isa delayed-punch hand right finger pinky
  )

(defp **attend-ship
  =goal> isa monitor
  =visual-location> isa visual-location - kind ship
  ==>
  +visual-location> isa visual-location kind ship
  )

(defp **initial-thrust-fast
  =goal> isa monitor
  =visual-location> isa visual-location kind ship velocity nil
  ?manual> state free
  ==>
  +manual> isa delayed-punch hand left finger middle delay fast 
  )

(defp **initial-thrust-slow
  =goal> isa monitor
  =visual-location> isa visual-location kind ship velocity nil
  ?manual> state free
  ==>
  +manual> isa delayed-punch hand left finger middle delay slow 
  )

;(defp **attend-shell
;  =goal> isa monitor
;  =visual-location> isa visual-location - kind shell
;  ==>
;  +visual-location> isa visual-location kind shell
;  )

;(defp **detect-shell-collision-course?
;  =goal> isa monitor
;  =visual-location> isa visual-location kind shell screenx =x
;  )

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defp **do-nothing
  =goal> isa avoid-fortress
  ==>
  =goal>
  )
(pdisable **do-nothing)

(defp **ship-thrust
  =goal> isa avoid-fortress
  ?manual> state free
  ==>
  =goal>
  +manual> isa delayed-punch hand left finger middle
  )
(pdisable **ship-thrust)
 
(defp **ship-turn-left
  =goal> isa avoid-fortress
  ?manual> state free
  ==>
  =goal>
  +manual> isa delayed-punch hand left finger ring
  )
(pdisable **ship-turn-left)

(defp **ship-turn-right
  =goal> isa avoid-fortress
  ?manual> state free
  ==>
  =goal>
  +manual> isa delayed-punch hand left finger index
  )
(pdisable **ship-turn-right)