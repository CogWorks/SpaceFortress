;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Helper functions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

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

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Model initialization
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

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
(chunk-type study-mine-letters state)
(chunk-type monitor)
(chunk-type shoot-fortress subgoal)
(chunk-type shoot-mine subgoal)
(chunk-type avoid-shells subgoal)
(chunk-type avoid-fortress subgoal)
(chunk-type avoid-warping subgoal)
(chunk-type avoid-mine subgoal)

;;; New chunk types
(chunk-type game-settings mines)
(chunk-type (token-location (:include visual-location)) orientation velocity)
(chunk-type (token-object (:include visual-object)) orientation velocity)
(chunk-type (ship (:include token-object)))
(chunk-type (fortress (:include token-object)))
(chunk-type (mine (:include token-object)))
(chunk-type (shell (:include token-object)))
(chunk-type (missile (:include token-object)))
(chunk-type (rect-location (:include visual-location)) top bottom left right)
(chunk-type (rect-object (:include visual-object)) top bottom left right)
(chunk-type (world-border (:include rect-object)))

(chunk-type mine-letters letter1 letter2 letter3)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Productions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defp **start**
  ?goal> buffer empty
  ?retrieval> buffer empty state free
  ==>
  +retrieval> isa game-settings
  )

(defp **study-mine-letters**
  ?goal> buffer empty
  =retrieval> isa game-settings - mines nil
  ?finger-check> right-pinkie free
  ==>
  =retrieval>
  +goal> isa study-mine-letters
  +manual> isa delayed-punch hand right finger pinky
  )

(defp **play-game**
  ?goal> buffer empty
  =retrieval> isa game-settings mines nil
  ?finger-check> right-pinkie free
  ==>
  =retrieval>
  +goal> isa monitor
  +manual> isa delayed-punch hand right finger pinky
  )

(defp **attend-ship**
  =goal> isa monitor
  =visual-location> isa visual-location - kind ship
  ==>
  +visual-location> isa visual-location kind ship
  )

(defp **initial-thrust**
  =goal> isa monitor
  =retrieval> isa game-settings
  =visual-location> isa visual-location kind ship velocity 0
  ?finger-check> left-middle free
  ==>
  -retrieval>
  +manual> isa delayed-punch hand left finger middle delay .15
  +goal> isa shoot-fortress
  +goal> isa avoid-fortress
  +goal> isa avoid-shells
  +goal> isa avoid-warping
  )

(defp **attend-border**
  =goal> isa avoid-warping subgoal nil
  ?imaginal> buffer empty
  ?visual-location> buffer empty
  ==>
  +visual-location> isa visual-location kind world-border
  )

(defp **imagine-border**
  =goal> isa avoid-warping subgoal nil
  ?imaginal> buffer empty
  =visual-location> isa visual-location kind world-border
  ==>
  +imaginal> =visual-location
  +visual-location> isa visual-location kind ship
  )

(defp **avoid-border-top-yes**
  =goal> isa avoid-warping subgoal nil
  =imaginal> isa visual-location kind world-border top =top
  =visual-location> isa visual-location kind ship screen-y =shipy
  !eval! (< (abs (- =top =shipy)) 150)
  ==>
  =goal> subgoal "avoid-top-turn"
  =visual-location>
  )

(defp **avoid-border-top-no**
  =goal> isa avoid-warping subgoal nil
  =imaginal> isa visual-location kind world-border top =top
  =visual-location> isa visual-location kind ship screen-y =shipy
  !eval! (> (abs (- =top =shipy)) 150)
  ==>
  -imaginal>
  -visual-location>
  )

(defp **avoid-top-border-perpendicular**
  =goal> isa avoid-warping subgoal "avoid-top-turn"
  =visual-location> isa visual-location kind ship orientation 90
  ?finger-check> left-index free
  ==>
  !eval! (buffer-chunk visual-location)
  +manual> isa delayed-punch hand left finger index delay .125
  +visual-location> isa visual-location kind ship
  )

(defp **avoid-top-border-turn-right**
  =goal> isa avoid-warping subgoal "avoid-top-turn"
  =visual-location> isa visual-location kind ship < orientation 90 > orientation 0
  ?finger-check> left-index free
  ==>
  +manual> isa delayed-punch hand left finger index delay .125
  +visual-location> isa visual-location kind ship
  )

(defp **avoid-top-border-turn-left**
  =goal> isa avoid-warping subgoal "avoid-top-turn"
  =visual-location> isa visual-location kind ship > orientation 90 < orientation 180
  ?finger-check> left-index free
  ==>
  +manual> isa delayed-punch hand left finger index delay .125
  +visual-location> isa visual-location kind ship
  )

(defp **avoid-top-border-thrust**
  =goal> isa avoid-warping subgoal "avoid-top-turn"
  =visual-location> isa visual-location kind ship > orientation 180 < orientation 360
  ?finger-check> left-middle free
  ==>
  +manual> isa delayed-punch hand left finger middle delay .2
  +visual-location> isa visual-location kind ship
  =goal> subgoal nil
  )

(defp find-mine-letters
 =goal> isa study-mine-letters state nil
==> 
 +visual-location> isa visual-location :attended nil kind text color "white"  < width 50
 +imaginal> isa mine-letters
 =goal> state find
 !eval! (print-visicon)
 )

(defp wait-for-letters
 =goal> isa study-mine-letters state find
 ?visual-location> state error
==>
 !eval! (print-visicon)
 +visual-location> isa visual-location :attended nil kind text color "white"  < width 50)

(defp read-letter
 =goal> isa study-mine-letters state find
 =visual-location> isa visual-location kind text
 ?visual> state free
==>
 +visual> isa move-attention screen-pos =visual-location
 =goal> state attend)

(defp attend-letter1
 =goal> isa study-mine-letters state attend
 =visual> isa text value =l
 =imaginal> isa mine-letters letter1 nil
==>
 +visual-location> isa visual-location kind text :attended nil color "white" < width 50
 =imaginal> letter1 =l
 =goal> state find)

(defp attend-letter2
 =goal> isa study-mine-letters state attend
 =visual> isa text value =l
 =imaginal> isa mine-letters letter1 =v letter2 nil
==>
 +visual-location> isa visual-location kind text :attended nil color "white"  < width 50
 =imaginal> letter2 =l
 =goal> state find)

(defp attend-letter3
 =goal> isa study-mine-letters state attend
 =visual> isa text value =l screen-pos =loc
 =imaginal> isa mine-letters letter1 =v letter2 =b letter3 nil
 ?finger-check> right-pinkie free
==>
 =imaginal> letter3 =l
 -imaginal>
 +manual> isa delayed-punch hand right finger pinky
 +goal> isa monitor)


 

 