;;ACT-R productions and support code
;;for the Pygame Space Fortress cognitive model



(defparameter *delay-time* 0.033)

(defmacro defp (&rest body)
  `(p-fct ',body))

(defmacro defp* (&rest body)
  `(p*-fct ',body))

(defun visicon-length ()
  (length (visicon-chunks (get-module :vision))))

(defun desired-vel-angle-by-position-deg (x y) ;;not used??
    "calculates angle ship should reach to enter orbiting circle around fortress using screen coordinates"
    (let ((distance (sqrt (+ (expt (- x 512) 2) (expt (- y 318) 2))))
          (angle-to-tan (asin (/ 100 (sqrt (+ (expt (- x 512) 2) (expt (- y 318) 2))))))
          (angle-from-x (atan2-rad (- 318 y) (- 512 x))))
        (if (< distance 100)
            (mod (- 120 (/ (* 3 distance) 14) (* angle-from-x 57.2957795)) 360) ;looking for a reason not to use LISP? Go infix!
            (mod (* 57.2957795 (- angle-to-tan angle-from-x)) 360))))
            
(defun desired-vel-angle-by-position-rad (x y) ;;;not used???
    "calculates angle ship should reach to enter orbiting circle around fortress using screen coordinates"
    (let ((angle-to-tan (asin (/ 92 (sqrt (+ (expt (- x 512) 2) (expt (- y 318) 2))))))
          (angle-from-x (atan2-rad (- 318 y) (- 512 x))))
        (- angle-to-tan angle-from-x)))
        

(defun desired-angle-deg (x y distance velx vely) ;we want the inverse of the vel vector added to the desired vector, which is 3 X |v|
    (let* ((vel-angle (atan2-rad vely velx))
          (speed (sqrt (+ (expt velx 2) (expt vely 2))))
          (ahead-x (+ x (* speed 15 (cos vel-angle))))
          (ahead-y (- y (* speed 15 (sin vel-angle))))
          (ahead-distance (sqrt (+ (expt (- ahead-x 512) 2) (expt (- ahead-y 318) 2))))
          (angle-to-tan (asin (/ 92 ahead-distance)))
          (angle-from-x (atan2-rad (- 318 ahead-y) (- 512 ahead-x)))
          (des-vel-angle (- angle-to-tan angle-from-x))
          (desx (- (* 3 (cos des-vel-angle)) velx))
          (desy (- (* 3 (sin des-vel-angle)) vely)))
       (if (< ahead-distance 92)
           ;180 - ? plus an additional 60 for center, scale up by 3x/14 to get to tangent (want to go from 120-? to 90-?)
           (mod (- 120 (/ (* 3 distance) 14) (* angle-from-x 57.2957795)) 360)
           (mod (* 57.2957795 (atan2-rad desy desx)) 360))))
           
(defun distance (x1 y1 x2 y2)
    (sqrt (+ (expt (- x1 x2) 2) (expt (- y1 y2) 2))))
            
(defun distance-to-fortress (x y)
    (distance x y 512 318))
   ; (sqrt (+ (expt (- x 512) 2) (expt (- y 318) 2)))) ;fortress is always at (355, 313) in world coords, (512, 318) in screen coords
    
(defun angle-to-fortress (x y)
    (mod (* (atan (- 318 y) (- 0 (- 512 x))) 57.2957795) 360)) 
    
(defun atan2-deg (y-vel x-vel)
    (if (and (= x-vel 0) (= y-vel 0))
        0
        (mod (* (atan y-vel x-vel) 57.2957795) 360))) ;manual convert to degrees
            
(defun atan2-rad (y-vel x-vel)
    (if (and (= x-vel 0) (= y-vel 0))
        0
        (atan y-vel x-vel))) 

(defun print-ship ()
  (let* ((chunks (get-visicon-chunks))
         (ship (first (remove nil (mapcar (lambda (x) 
                                            (if (eql 'sf-visual-location 
                                                     (act-r-chunk-type-name (act-r-chunk-chunk-type (get-chunk x)))) 
                                                (get-chunk x)))
                                          chunks)))))
    (if ship (maphash (lambda(k v) (print (list k v))) (act-r-chunk-slot-value-lists ship)))))



(defmethod vis-loc-to-obj :around ((instance json-interface-module) vis-loc)
  (let ((obj (call-next-method)))
    (format t "~%~S ~S ~S ~S" obj vis-loc (get-chunk obj) (get-chunk vis-loc))
    (break))
  (let* ((chunks (get-visicon-chunks))
         (ship (first (remove nil (mapcar (lambda (x) 
                                            (if (eql 'sf-visual-location 
                                                     (act-r-chunk-type-name (act-r-chunk-chunk-type (get-chunk x)))) 
                                                (get-chunk x)))
                                          chunks)))))
    (when ship 
      (let* ((slot-values (act-r-chunk-slot-value-lists ship))
             (x (gethash 'SCREEN-X slot-values))
             (y (gethash 'SCREEN-Y slot-values))
             (orient (gethash 'VALUE slot-values))
             (velx (gethash 'VEL_X slot-values))
             (vely (gethash 'VEL_Y slot-values))
             fd a-to-f da va)
#|        
                     (FORTRESS_EXIST T)  ;;;
                     (MINE-EXIST 0) ;;;
                     (VLNER 0) ;;;
                     (BONUS-EXIST 0) ;;;
|#           
        (setf (gethash 'vel slot-values) (sqrt (+ (expt velx 2) (expt vely 2))))
        (setf (gethash 'vel-angle slot-values) (setq va (atan2-deg vely velx)))
        (setf (gethash 'angle-from-fort slot-values) (setq a-to-f (angle-to-fortress x y)))
        (setf (gethash 'fortress-distance slot-values) (setq fd (distance-to-fortress x y)))
        (setf (gethash 'des-angle slot-value) (setq da (desired-angle-deg x y  fd  velx vely)))
        (setf (gethash 'vel-accuracy slot-values) (mod (abs (- da va)) 360))
        (setf (gethash 'des-diff slot-values) (mod (- da orient) 360))
        (setf (gethash 'orient-diff slot-values) (mod (- orient a-to-f ) 360))
))))
        
        
        

(clear-all)

(define-model sf5

;:default-punch-delay uses the new delayed-punch technique, to send separate keydown and keyup events to the game
;default is set to 60ms, which reflects average length keytaps from expert players
;:mas set to turn on spreading activation to hasten foe letter retrievals
;:bll increased to speed retrieval times
;:lf lowered to speed retrieval times
;:visual-movement-tolerance dramatically increased due to mine wrapping around the screen
;:visual-attention-latency lowered due to well-practiced attention shifts to known locations
;:do-not-harvest imaginal will keep mine appearances always available
(sgp :esc t :er t :v t :mas 1 :bll 0.5 :ans 0.25 :lf .5 :visual-movement-tolerance 40.0 :trace-detail high :test-feats nil :motor-feature-prep-time 0 :default-punch-delay 0.06 :visual-attention-latency 0.05 :do-not-harvest imaginal
:jni-hostname "localhost" :jni-port 5555 :jni-sync t
)


(chunk-type foe-letters-type letter1 letter2 letter3)
(chunk-type read-foe-letters-type state)
(chunk-type handle-mine state iff letter1 letter2 letter3)
(chunk-type handle-bonus state)
(chunk-type symbol-record state mine-exist bonus-exist ship-exist last-goal symbol-attended)
(chunk-type fly-ship state posx posy velx vely angle vel-angle angle-from-fort fortress-distance fortress-exist vlner vel-diff orient-diff)
(chunk-type standard-flight-pattern-type state shipx shipy shipangle targetangle)
(chunk-type (game-object (:include visual-object)) (kind nil))
(chunk-type (foe-letter (:include game-object)))
(chunk-type (ship (:include game-object)) (vel_x 0) (vel_y 0) (vel 0) (vel-angle 0) (vel-accuracy 0) (angle-from-fort 181) (fortress-distance 110) (fortress_exist 1) (vlner 0) (vel-diff 0) (orient-diff 0) (des-angle 0) (des-diff 0) (mine-exist 0) (bonus-exist 0)) 
(chunk-type (sf-visual-location (:include visual-location)) (vel_x 0) (vel_y 0)  (fortress_exist 1) (vlner 0)  (mine-exist 0) (bonus-exist 0))
(chunk-type (fortress (:include game-object)))
(chunk-type (shell (:include game-object)))
(chunk-type (iff (:include game-object)))
(chunk-type (mine-loc-type (:include visual-location)) (mine-angle-diff 0) (mine-distance 0))
(chunk-type (mine (:include game-object)) (mine-angle-diff 0) (mine-distance 0))
(chunk-type (bonus (:include game-object)))
(chunk-type (pnts (:include game-object)))
(chunk-type (vlcty (:include game-object)))
(chunk-type (speed (:include game-object)))
(chunk-type (cntrl (:include game-object)))
(chunk-type (vlner (:include game-object)))
(chunk-type (shots (:include game-object)))
(chunk-type (intrvl (:include game-object)))
(chunk-type idle state)

(define-chunks (global-visual isa symbol-record state "not-expecting-bonus" mine-exist 0 bonus-exist 0 ship-exist 0 last-goal "none" symbol-attended "not-attended"))

(add-dm (read-foe-letters isa read-foe-letters-type state "not-reading")
        (ship-obj isa ship)
        (fortress-obj isa fortress)
        (shell-obj isa shell)
        (iff-obj isa iff)
        (mine-obj isa mine)
        (bonus-obj isa bonus)
        (pnts-obj isa pnts)
        (vlcty-obj isa vlcty)
        (cntrl-obj isa cntrl)
        (vlner-obj isa vlner)
        (speed-obj isa speed)
        (shots-obj isa shots)
        (intrvl-obj isa intrvl)
        (ship-loc isa sf-visual-location screen-x 0 screen-y 0 value 90 kind ship) ;value refers to orientation
        (fortress-loc isa visual-location screen-x 512 screen-y 318 value 90 kind fortress) ;value refers to orientation
        (shell-loc isa visual-location screen-x 0 screen-y 0 kind shell)
        (mine-loc isa mine-loc-type screen-x 0 screen-y 0 kind mine)
        (bonus-loc isa visual-location screen-x 512 screen-y 395 value "" kind bonus) ;value refers to symbol
        (pnts-loc isa visual-location screen-x 205 screen-y 680 value 0 kind pnts)
        (cntrl-loc isa visual-location screen-x 292 screen-y 680 value 0 kind cntrl)
        (vlcty-loc isa visual-location screen-x 379 screen-y 680 value 0 kind vlcty)
        (vlner-loc isa visual-location screen-x 465 screen-y 680 value 0 kind vlner)
        (iff-loc isa visual-location screen-x 553 screen-y 680 value "-" kind iff)
        (intrvl-loc isa visual-location screen-x 641 screen-y 680 value 0 kind intrvl)
        (speed-loc isa visual-location screen-x 729 screen-y 680 value 0 kind speed)
        (shots-loc isa visual-location screen-x 819 screen-y 680 value 0 kind shots)
        (a isa chunk) (b isa chunk) (c isa chunk) (d isa chunk) (e isa chunk) (f isa chunk)
        (g isa chunk) (h isa chunk) (i isa chunk) (j isa chunk) (k isa chunk) (l isa chunk)
        (m isa chunk) (n isa chunk) (o isa chunk) (p isa chunk) (q isa chunk) (r isa chunk)
        (s isa chunk) (t isa chunk) (u isa chunk) (v isa chunk) (w isa chunk) (x isa chunk)      
        (y isa chunk) (z isa chunk)
        (start isa chunk)
        (idle0 isa idle)) 

(goal-focus idle0) ;;;read-foe-letters)
        
;try to keep distance between 88 and 96
;new motor commands allow:
;             
; +manual>
;   isa hold-key
;   hand <left | right>
;   finger <index | middle |ring | pinkie | thumb>
; 
; +manual>
;   isa release-key
;   hand <left | right>
;   finger <index | middle |ring | pinkie | thumb>
; 
; +manual>
;   isa delayed-punch
;   hand <left | right>
;   finger <index | middle |ring | pinkie | thumb>    (defaults to .06 as reflected in (sgp))
;
;but not specifically "key 'a'"

;new motor query:
; ?finger-check>
;   left-middle {busy|free}

;;make sure that the production that hits Enter for foe_mines calls (start-sim)

;Based on least-square estimations of fit between model and data, Taatgen and Van Rijn estimated the following values for three
;model parameters: 11 ms for startpulse, 1.1 for a, and 0.015 for b
;t_n+1 = at_n + noise(M=0, SD = b * at_n)

;;;;
(p wait-for-game
 =goal> isa idle state nil
==>
 )

(p start-flying
 =goal> isa idle state nil
 ?visual-location> buffer unrequested 
==>
 +goal> isa fly-ship
        state       "look-for-ship")

(spp start-flying :u 10)

;;;;;;;;;;;;;;;;;;;;;;;
;;READING PRODUCTIONS;;
;;;;;;;;;;;;;;;;;;;;;;;

(p start-reading-letters
    =goal>
        ISA         read-foe-letters-type
        state       "not-reading"
==>
    =goal>
        state       "reading-letter1"
    +visual-location>
        ISA         visual-location
        kind        foe-letter
        < screen-x  500 ;first letter at (425 375)
)

(p attend-first-letter
    =goal>
        ISA         read-foe-letters-type
        state       "reading-letter1"
    =visual-location>
        ISA         visual-location
        kind        foe-letter
    ?visual>
        state       free
==>
    =goal>
        state       "encoding-letter1"
    +visual>
        ISA         move-attention
        screen-pos  =visual-location
)

(p encode-first-letter
    =goal>
        ISA         read-foe-letters-type
        state       "encoding-letter1"
    =visual>
        ISA         visual-object
        value       =letter
==>
    +imaginal>
        ISA         foe-letters-type
        letter1     =letter
    +visual-location>
        ISA         visual-location
        kind        foe-letter
        > screen-x  500 ;second letter at (515 375)
        < screen-x  550
    =goal>
        state       "reading-letter2"
)

(p attend-second-letter
    =goal>
        ISA         read-foe-letters-type
        state       "reading-letter2"
    =visual-location>
        ISA         visual-location
        kind        foe-letter
    ?visual>
        state       free
    =imaginal>
        ISA         foe-letters-type
==>
    =goal>
        state       "encoding-letter2"
    =imaginal>
    +visual>
        ISA         move-attention
        screen-pos  =visual-location
)

(p encode-second-letter
    =goal>
        ISA         read-foe-letters-type
        state       "encoding-letter2"
    =visual>
        ISA         visual-object
        value       =letter
    =imaginal>
        ISA         foe-letters-type
==>
    =goal>
        state       "reading-letter3"
    =imaginal>
        letter2     =letter
    +visual-location>
        ISA         visual-location
        kind        foe-letter
        > screen-x  600 ;third letter at (605 375)
)

(p attend-third-letter
    =goal>
        ISA         read-foe-letters-type
        state       "reading-letter3"
    =visual-location>
        ISA         visual-location
        kind        foe-letter
    ?visual>
        state       free
    =imaginal>
        ISA         foe-letters-type
==>
    =goal>
        state       "encoding-letter3"
    =imaginal>
    +visual>
        ISA         move-attention
        screen-pos  =visual-location
)

(p encode-third-letter
    =goal>
        ISA         read-foe-letters-type
        state       "encoding-letter3"
    =visual>
        ISA         visual-object
        value       =letter
    =imaginal>
        ISA         foe-letters-type
==>
    =goal>
        state       "rehearsal1"
    =imaginal>
        letter3     =letter
    -imaginal>
)

(p first-rehearsal
    =goal>
        ISA         read-foe-letters-type
        state       "rehearsal1"
    ?retrieval>
        state       free
    ?imaginal>
        buffer      empty
==>
    +retrieval>
        ISA         foe-letters-type
    =goal>
        state       "retrieving1"
)

(p first-recall
    =goal>
        ISA         read-foe-letters-type
        state       "retrieving1"
    =retrieval>
        ISA         foe-letters-type
==>
    =goal>
        state       "rehearsal2"
)

(p second-rehearsal
    =goal>
        ISA         read-foe-letters-type
        state       "rehearsal2"
    ?retrieval>
        state       free
==>
    +retrieval>
        ISA         foe-letters-type
    =goal>
        state       "retrieving2"
)

(p second-recall
    =goal>
        ISA         read-foe-letters-type
        state       "retrieving2"
    =retrieval>
        ISA         foe-letters-type
==>
    =goal>
        state       "rehearsal3"
)

(p third-rehearsal
    =goal>
        ISA         read-foe-letters-type
        state       "rehearsal3"
    ?retrieval>
        state       free
==>
    +retrieval>
        ISA         foe-letters-type
    =goal>
        state       "retrieving3"
)

(p third-recall
    =goal>
        ISA         read-foe-letters-type
        state       "retrieving3"
    =retrieval>
        ISA         foe-letters-type
==>
    =goal>
        state       "done-reading"
)

(p start-sim
    =goal>
        ISA         read-foe-letters-type
        state       "done-reading"
==>
    +goal>
        ISA         fly-ship
        state       "begin"
    !safe-eval!     (start-sim)
)

(p begin-flying
    =goal>
        ISA         fly-ship
        state       "begin"
==>
    =goal>
        state       "look-for-ship"
    +visual-location>
        ISA         visual-location
        kind        ship  
)

(p find-ship
    =goal>
        ISA         fly-ship
        state       "look-for-ship"
    =visual-location>
        ISA         visual-location
        kind        ship
        screen-x    =x
        screen-y    =y
    ?visual>
        state       free
==>
    =goal>
        state       "track-the-ship"
        posx        =x
        posy        =y
    +visual>
        ISA         move-attention
        screen-pos  =visual-location
)

(p track-ship
    =goal>
        ISA         fly-ship
        state       "track-the-ship"
    =visual>
        ISA         ship
==>
    =goal>
        state       "standard-flight-pattern"

;Causing vis-loc buffer to always be full, disallowing buffer stuffing
   +visual>
       ISA         start-tracking

)

#|(p mine-error-visloc
   =goal>
       ISA         handle-mine
   ?visual-location>
       state       error
==>
   -goal>
   +goal>
       ISA         fly-ship
       state       "ship-destroyed"
   +visual-location>
       ISA         visual-location
       kind        ship
)|#

#|(p mine-error-visual
   =goal>
       ISA         handle-mine
   ?visual>
       state       error
==>
   -goal>
   +visual>
       ISA         clear
   +goal>
       ISA         fly-ship
       state       "ship-destroyed"
   +visual-location>
       ISA         visual-location
       kind        ship
)|#

#|(p mine-error-visual-2 ;shouldn't happen, but...
   =goal>
       ISA         handle-mine
       state       "track-mine"
   =visual-location>
       ISA         visual-location
       kind        ship
==>
   -goal>
   +visual>
       ISA         clear
   +goal>
       ISA         fly-ship
       state       "track-the-ship"
    +visual>
        ISA         move-attention
        screen-pos  =visual-location
)|#

;(p ship-error-visloc
;   =goal>
;       ISA         fly-ship
;   ?visual-location>
;       state       error
;==>
;   =goal>
;       state       ship-destroyed
;   +visual-location>
;       ISA         visual-location
;       kind        ship
;)

#|(p ship-error-visual
   =goal>
       ISA         fly-ship
   ?visual>
       state       error
==>
   +visual>
       ISA         clear
   =goal>
       state       "ship-destroyed"
   +visual-location>
       ISA         visual-location
       kind        ship
)|#

#|(p should-be-looking-at-ship
   =goal>
       ISA        fly-ship
   =visual-location>
       ISA        visual-location
       - kind     ship
==>
   +visual>
       ISA        clear
   +visual-location>
       ISA        visual-location
       kind       ship
   =goal>
       state      "ship-destroyed"
)|#

(p ship-destroyed-during-flight
   =goal>
       ISA        fly-ship
   =imaginal>
       ISA        symbol-record
       = ship-exist 0
==>
   =goal>
       state      "ship-destroyed"
   +visual>
       ISA        clear
   +visual-location>
       ISA        visual-location
       kind       ship
)

(p ship-destroyed-during-mine
   =goal>
       ISA        handle-mine
   =imaginal>
       ISA        symbol-record
       = ship-exist 0
==>
   +goal>
       ISA        fly-ship
       state      "ship-destroyed"
   +visual>
       ISA        clear
   +visual-location>
       ISA        visual-location
       kind       ship
)

(p ship-destroyed-during-bonus
   =goal>
       ISA        handle-bonus
   =imaginal>
       ISA        symbol-record
       = ship-exist 0
==>
   +goal>
       ISA        fly-ship
       state      "ship-destroyed"
   +visual>
       ISA        clear
   +visual-location>
       ISA        visual-location
       kind       ship
)

(p ship-destroyed-keep-looking
   =goal>
       ISA        fly-ship
       state      "ship-destroyed"
   ?visual-location>
       state      error
==>
   =goal>
   +visual-location>
       ISA         visual-location
       kind        ship
)

(p ship-destroyed-and-found
   =goal>
       ISA        fly-ship
       state      "ship-destroyed"
    =visual-location>
        ISA         visual-location
        kind        ship
        screen-x    =x
        screen-y    =y
    ?visual>
        state       free
==>
    =goal>
        state       "track-the-ship"
        posx        =x
        posy        =y
    +visual>
        ISA         move-attention
        screen-pos  =visual-location
)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;STANDARD-FLIGHT PRODUCTIONS;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;;Depending on position and velocity, turn and thrust ship to stay in  circle facing the fortress

; (p find-ship-within-fly-ship-goal
;     =goal>
;         ISA         fly-ship
;     =visual-location>
;         ISA         visual-location
;         kind        ship
;     ?visual>
;         buffer      empty
; ==>   
;     =goal>
;         state       track-the-ship
;     +visual>
;         ISA         move-attention
;         screen-pos  =visual-location 
; )
; 
; (p find-ship-within-handle-mine-goal
;     =goal>
;         ISA         handle-mine
;     =visual-location>
;         ISA         visual-location
;         kind        ship
;     ?visual>
;         buffer      empty
; ==>   
;     -goal>
;     +goal>
;         ISA         fly-ship
;         state       track-the-ship
;     +visual>
;         ISA         move-attention
;         screen-pos  =visual-location 
; )
; 
; (p find-ship-within-handle-bonus-goal
;     =goal>
;         ISA         handle-bonus
;     =visual-location>
;         ISA         visual-location
;         kind        ship
;     ?visual>
;         buffer      empty
; ==>   
;     -goal>
;     +goal>
;         ISA         fly-ship
;         state       track-the-ship
;     +visual>
;         ISA         move-attention
;         screen-pos  =visual-location 
; )

(p start-initial-thrust
    =goal>
        ISA         fly-ship
        state       "standard-flight-pattern"
    =visual>
        ISA         ship
        = vel       0
==>
    +manual>
        ; ISA         press-key
        ; key         s ;prevents hand from moving, sends a "w" to the game
        ISA         hold-key
        hand        left
        finger      middle
    +temporal>
        ISA         time ;start the "counter" for in-between-shots
    =goal>
        state       "initial-thrust"
)

(p start-initial-thrust-nil
    =goal>
        ISA         fly-ship
        state       "standard-flight-pattern"
    =visual>
        ISA         ship
        = vel       nil
==>
    +manual>
        ; ISA         press-key
        ; key         s ;prevents hand from moving, sends a "w" to the game
        ISA         hold-key
        hand        left
        finger      middle
    +temporal>
        ISA         time ;start the "counter" for in-between-shots
    =goal>
        state       "initial-thrust"
)

(p stop-initial-thrust
    =goal>
        ISA         fly-ship
        state       "initial-thrust"
    =temporal>
        ISA         time
        > ticks     7
==>
    +manual>
        ISA         release-key
        hand        left
        finger      middle
    +temporal>
        ISA         time
    =goal>
        state       "start-initial-turn"
)

(p start-initial-turn
    =goal>
        ISA         fly-ship
        state       "start-initial-turn"
    ?manual>
        processor   free
==>
    =goal>
        state       "initial-turn"
    +manual>
        ISA         hold-key
        hand        left
        finger      index
    +temporal>
        ISA         time
)

(p stop-initial-turn
    =goal>
        ISA         fly-ship
        state       "initial-turn"
    =temporal>
        ISA         time
        > ticks     16
==>
    +manual>
        ISA         release-key
        hand        left
        finger      index
    +temporal>
        ISA         time
    =goal>
        state       "standard-flight-pattern"
)

(p hold-right-in-circle
    =goal>
        ISA         fly-ship
        state       "standard-flight-pattern"
    =visual>
        ISA         ship
        >= orient-diff   190
        - vel     0
        > fortress-distance 95;90
        < fortress-distance 190;210
    ?finger-check>
        left-index  free
==>
    +manual>
        ISA         hold-key
        hand        left
        finger      index
)

(p release-right-in-circle
    =goal>
        ISA         fly-ship
        state       "standard-flight-pattern"
    =visual>
        ISA         ship
        < orient-diff   190
        >= orient-diff  182
        - vel     0
        > fortress-distance 95;90
        < fortress-distance 190;210
    ?finger-check>
        left-index  busy
==>
    +manual>
        ISA         release-key
        hand        left
        finger      index
)

(p tap-right-in-circle
    =goal>
        ISA         fly-ship
        state       "standard-flight-pattern"
    =visual>
        ISA         ship
        > orient-diff   182; 185
        <= orient-diff 190
        - vel     0
        > fortress-distance 95;90 ;95 ;88
        < fortress-distance 190;210 ;180
;     ?manual>
;        processor       free
    ?finger-check>
        left-index  free
==>
    +manual>
        ;ISA         press-key
        ;key         d
        ISA         delayed-punch
        hand        left
        finger      index
)

(p turn-left-in-circle
    =goal>
        ISA         fly-ship
        state       "standard-flight-pattern"
    =visual>
        ISA         ship
        < orient-diff   162; 185
        - vel     0
        > fortress-distance 95;90 ;95 ;88
        < fortress-distance 190;210 ;180
;     ?manual>
;        processor       free
    ?finger-check>
        left-ring   free
==>
    +manual>
        ;ISA         press-key
        ;key         a
        ISA         delayed-punch
        hand        left
        finger      ring
)

(p thrust-in-circle
    =goal>
        ISA         fly-ship
        state       "standard-flight-pattern"
    =visual>
        ISA         ship
        - vel       0
        ;< vel       2 ;NEW
        > vel-diff  275
        > fortress-distance 95;90 ;95 
        < fortress-distance 175;210 ;180
        > orient-diff 185 
     ;?manual>
     ;    processor  free
     ?finger-check>
        left-middle free
==>
    +manual>
        ;ISA         press-key
        ;key         s  ;prevents hand from moving - sends a "w" to the game
        ISA         delayed-punch
        hand        left
        finger      middle
)

(p tap-right-outside-circle
   =goal>
     ISA    fly-ship
     state  "standard-flight-pattern"
   =visual>
     ISA    ship
     - vel  0
     >= fortress-distance 190;210 ;180
     >= des-diff 180
     <= des-diff 355
   ?finger-check>
     left-index  free
==>
   +manual>
     ISA         delayed-punch
     hand        left
     finger      index
)

#|(p hold-right-outside-circle
   =goal>
     ISA    fly-ship
     state  "standard-flight-pattern"
   =visual>
     ISA    ship
     - vel  0
     >= fortress-distance 210
     > des-diff 225
     <= des-diff 355
   ?finger-check>
     left-index  free
==>
   +manual>
     ISA         hold-key
     hand        left
     finger      index
)

(p release-right-outside-circle
   =goal>
     ISA    fly-ship
     state  "standard-flight-pattern"
   =visual>
     ISA    ship
     - vel  0
     >= fortress-distance 210
     <= des-diff 225
   ?finger-check>
     left-index  busy
==>
   +manual>
     ISA         release-key
     hand        left
     finger      index
)|#

(p turn-left-outside-circle
   =goal>
     ISA    fly-ship
     state  "standard-flight-pattern"
   =visual>
     ISA    ship
     - vel  0
     >= fortress-distance 190;210 ;180
     < des-diff 180
     >= des-diff 5
   ?finger-check>
     left-ring  free
==>
   +manual>
     ISA         delayed-punch
     hand        left
     finger      ring
)

(p thrust-outside-circle-1
   =goal>
     ISA    fly-ship
     state  "standard-flight-pattern"
   =visual>
     ISA    ship
     - vel  0
     >= fortress-distance 175;210 ;180
     < des-diff 360
     > des-diff 355
     > vel-accuracy 20 ;acts as speed limit - don't thrust if we're moving close enough in the desired direction
   ?finger-check>
     left-middle  free
==>
   +manual>
     ISA         delayed-punch
     hand        left
     finger      middle
)

(p thrust-outside-circle-2
   =goal>
     ISA    fly-ship
     state  "standard-flight-pattern"
   =visual>
     ISA    ship
     - vel  0
     >= fortress-distance 175;210 ;180
     >= des-diff 0
     < des-diff 5
     > vel-accuracy 20
   ?finger-check>
     left-middle  free
==>
   +manual>
     ISA         delayed-punch
     hand        left
     finger      middle
)

#|(p turn-right-too-close
    =goal>
        ISA         fly-ship
        state       "standard-flight-pattern"
    =visual>
        ISA         ship
        > orient-diff   182; 185
        - vel     0
        < fortress-distance 95 ;88
     ;?manual>
     ;   processor       free
    ?finger-check>
        left-index  free
==>
    +manual>
        ;ISA         press-key
        ;key         d
        ISA         delayed-punch
        hand        left
        finger      index
)

(p thrust-too-close
    =goal>
        ISA         fly-ship
        state       "standard-flight-pattern"
    =visual>
        ISA         ship
        - vel       0
        > vel-diff  270 ;288 ;276.3
        < fortress-distance 95 ;70 ;88
        > orient-diff 195 ;don't want to thrust into the fortress
     ;?manual>
     ;    processor  free
     ?finger-check>
        left-middle free
==>
    +manual>
        ;ISA         press-key
        ;key         s  ;prevents hand from moving - sends a "w" to the game
        ISA         delayed-punch
        hand        left
        finger      middle
)|#

;;;;;;;;;;;;;;;;;;;;
;;FIRE ON FORTRESS;;
;;;;;;;;;;;;;;;;;;;;

(p fire
    =goal>
        ISA         fly-ship
        state       "standard-flight-pattern"
    =visual>
        ISA         ship
        > orient-diff 176
        < orient-diff 184
        < fortress-distance 180
        = fortress_exist    1
        < vlner         10
    ?finger-check>
        left-thumb  free
    =temporal>
        ISA         time
        > ticks     16 ;16 works but seems excessively fast
==>
    +manual>
        ISA         delayed-punch
        hand        left
        finger      thumb
    +temporal>
        ISA         time
)

(p fire-first-of-second
        =goal>
            ISA         fly-ship
            state       "standard-flight-pattern"
        =visual>
            ISA         ship
            > orient-diff 176
            < orient-diff 184
            < fortress-distance 180
            = fortress_exist    1
            >= vlner        10
        ?finger-check>
            left-thumb  free
        =temporal>
            ISA         time
            > ticks     12
    ==>
        +manual>
            ISA         delayed-punch
            hand        left
            finger      thumb
        =goal>
            state       "fire-again"
)

(p fire-second-of-second
    =goal>
        ISA         fly-ship
        state       "fire-again"
    ?finger-check>
        left-thumb  free
==>
    +manual>
        ISA         delayed-punch
        hand        left
        finger      thumb
    =goal>
        state       "standard-flight-pattern"
    +temporal>
        ISA         time
)

;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;HANDLE MINE PRODUCTIONS;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;

(p see-new-mine
    =goal>
        ISA         fly-ship
        state       "standard-flight-pattern"
    =imaginal>
        ISA         symbol-record
        = mine-exist 1
;    =visual>
;        ISA         ship
;        = mine-exist 1
    ?finger-check>
        left-index  free
        left-middle free
        left-ring   free
==>
    +visual>
        ISA         clear ;stop tracking
    +visual-location>
        ISA         visual-location
        kind        iff
    +goal>
        ISA         handle-mine
        state       "find-iff"
    +retrieval>
        ISA         foe-letters-type
        - letter1   nil
        - letter2   nil
        - letter3   nil
    !safe-eval! (model-output "Noticed a mine")
)

(p see-new-mine-release-thrust
    =goal>
        ISA         fly-ship
        state       "standard-flight-pattern"
    =imaginal>
        ISA         symbol-record
        = mine-exist 1
    ?finger-check>
        left-middle  busy
==>
    +manual>
        ISA         release-key
        hand        left
        finger      middle
)

(p see-new-mine-release-right
    =goal>
        ISA         fly-ship
        state       "standard-flight-pattern"
    =imaginal>
        ISA         symbol-record
        = mine-exist 1
    ?finger-check>
        left-index  busy
==>
    +manual>
        ISA         release-key
        hand        left
        finger      index
)

(p see-new-mine-release-left
    =goal>
        ISA         fly-ship
        state       "standard-flight-pattern"
    =imaginal>
        ISA         symbol-record
        = mine-exist 1
    ?finger-check>
        left-ring   busy
==>
    +manual>
        ISA         release-key
        hand        left
        finger      ring
)

(p attend-iff
    =goal>
       ISA          handle-mine
       state        "find-iff"
   =visual-location>
       ISA          visual-location
       kind         iff
==>
    +visual>
        ISA         move-attention
        screen-pos  =visual-location
    =goal>
        state       "encode-iff"
)

(p encode-iff
    =goal>
        ISA         handle-mine
        state       "encode-iff"
    =visual>
        ISA         visual-object
        value       =tag
==>
    =goal>
        iff         =tag
        state       "set-letters"
    +visual-location> ;look at mine right away while waiting for retrieval
        ISA         visual-location
        kind        mine
)

(p attend-mine-waiting-for-retrieval
    =goal>
        ISA         handle-mine
        state       "set-letters"
    ?retrieval>
        buffer      empty
    =visual-location>
        ISA         visual-location
        kind        mine
    =visual>
        ISA         game-object
        - kind      mine
==>
    =goal>
    +visual>
        ISA         move-attention
        screen-pos  =visual-location
)

(p attend-mine-waiting-for-retrieval-2
    =goal>
        ISA         handle-mine
        state       "set-letters"
    ?retrieval>
        buffer      empty
    =visual-location>
        ISA         visual-location
        kind        mine
    ?visual>
        buffer      empty
==>
    =goal>
    +visual>
        ISA         move-attention
        screen-pos  =visual-location
)

(p hold-left-waiting-for-retrieval
    =goal>
        ISA         handle-mine
        state       "set-letters"
    ?retrieval>
        buffer      empty
    =visual>
        ISA         mine
        > mine-angle-diff 180
        < mine-angle-diff 315
    ?finger-check>
        left-ring   free
==>
    =goal>
    +manual>
        ISA         hold-key
        hand        left
        finger      ring
)

(p hold-right-waiting-for-retrieval
    =goal>
        ISA         handle-mine
        state       "set-letters"
    ?retrieval>
        buffer      empty
    =visual>
        ISA         mine
        <= mine-angle-diff 180
        > mine-angle-diff 45
    ?finger-check>
        left-index  free
==>
    =goal>
    +manual>
        ISA         hold-key
        hand        left
        finger      index
)

(p release-left-waiting-for-retrieval
    =goal>
        ISA         handle-mine
        state       "set-letters"
    =visual>
        ISA         mine
        >= mine-angle-diff 315
    ?finger-check>
        left-ring   busy
==>
    =goal>
    +manual>
        ISA         release-key
        hand        left
        finger      ring
)

(p release-right-waiting-for-retrieval
    =goal>
        ISA         handle-mine
        state       "set-letters"
    =visual>
        ISA         mine
        <= mine-angle-diff 45
    ?finger-check>
        left-index  busy
==>
    =goal>
    +manual>
        ISA         release-key
        hand        left
        finger      index
)

(p tap-left-waiting-for-retrieval
    =goal>
        ISA         handle-mine
        state       "set-letters"
    ?retrieval>
        buffer      empty
    =visual>
        ISA         mine
        >= mine-angle-diff 315
        < mine-angle-diff 345
    ?finger-check>
        left-ring   free
==>
    =goal>
    +manual>
        ISA         delayed-punch
        hand        left
        finger      ring
)

(p tap-right-waiting-for-retrieval
    =goal>
        ISA         handle-mine
        state       "set-letters"
    ?retrieval>
        buffer      empty
    =visual>
        ISA         mine
        <= mine-angle-diff 45
        > mine-angle-diff 15
    ?finger-check>
        left-index  free
==>
    =goal>
    +manual>
        ISA         delayed-punch
        hand        left
        finger      index
)

(p set-mine-letters
    =goal>
        ISA         handle-mine
        state       "set-letters"
    =retrieval>
        ISA         foe-letters-type
        letter1     =l1
        letter2     =l2
        letter3     =l3
==>
    =goal>
        state       "determine-friend-or-foe"
        letter1     =l1
        letter2     =l2
        letter3     =l3
    +manual>
        ISA         release-key
        hand        left
        finger      index
    +manual>
        ISA         release-key
        hand        left
        finger      ring
)

(p mine-is-a-friend
    =goal>
        ISA         handle-mine
        state       "determine-friend-or-foe"
        iff         =tag
        - letter1   =tag
        - letter2   =tag
        - letter3   =tag
==>
    !safe-eval!     (model-output "Mine is a friend")
    =goal>
        state       "find-mine"
    +visual-location>
        ISA         visual-location
        kind        mine
)

(p mine-is-a-foe-1
    =goal>
        ISA         handle-mine
        state       "determine-friend-or-foe"
        iff         =tag
        = letter1   =tag
==>
    !safe-eval!     (model-output "Mine is a foe")
    =goal>
        state       "tag-mine"
)

(p mine-is-a-foe-2
    =goal>
        ISA         handle-mine
        state       "determine-friend-or-foe"
        iff         =tag
        = letter2   =tag
==>
    !safe-eval!     (model-output "Mine is a foe")
    =goal>
        state       "tag-mine"
)

(p mine-is-a-foe-3
    =goal>
        ISA         handle-mine
        state       "determine-friend-or-foe"
        iff         =tag
        = letter3   =tag
==>
    !safe-eval!     (model-output "Mine is a foe")
    =goal>
        state       "tag-mine"
)

(p first-intrvl-tag
    =goal>
        ISA         handle-mine
        state       "tag-mine"
==>
    +manual>
        ISA         delayed-punch
        hand        right
        finger      index
    +temporal>
        ISA         time
    =goal>
        state       "intrvl"
)

(p second-intrvl-tag
    =goal>
        ISA         handle-mine
        state       "intrvl"
    =temporal>
        ISA         time
        >= ticks     12
==>
    +manual>
        ISA         delayed-punch
        hand        right
        finger      index
    +temporal>
        ISA         time
    =goal>
        state       "find-mine"
    +visual-location>
        ISA         visual-location
        kind        mine
)

(p attend-mine
    =goal>
        ISA         handle-mine
        state       "find-mine"
    =visual-location>
        ISA         visual-location
        kind        mine
==>
    =visual-location> ;sometimes clears visual along with itself, preventing track-mine
    +visual>
        ISA         move-attention
        screen-pos  =visual-location
    =goal>
        state       "track-mine"
)

(p track-mine
    =goal>
        ISA         handle-mine
        state       "track-mine"
    =visual>
        ISA         mine
==>
    +visual>
        ISA         start-tracking
    =goal>
        state       "shoot-mine"
)

(p tap-right-to-face-mine
    =goal>
        ISA         handle-mine
        state       "shoot-mine"
    =visual>
        ISA         mine
         <= mine-angle-diff 180
         > mine-angle-diff 12
    ?finger-check>
        left-index  free
==>
    +manual>
        ISA         delayed-punch
        hand        left
        finger      index
)

(p hold-right-to-face-mine
    =goal>
        ISA         handle-mine
        state       "shoot-mine"
    =visual>
        ISA         mine
         <= mine-angle-diff 180
         > mine-angle-diff 24
    ?finger-check>
        left-index  free
==>
    +manual>
        ISA         hold-key
        hand        left
        finger      index
)

(p release-right-to-face-mine
    =goal>
        ISA         handle-mine
        state       "shoot-mine"
    =visual>
        ISA         mine
         >= mine-angle-diff 12
         <= mine-angle-diff 24
    ?finger-check>
        left-index  busy
==>
    +manual>
        ISA         release-key
        hand        left
        finger      index
)

(p tap-left-to-face-mine
    =goal>
        ISA         handle-mine
        state       "shoot-mine"
    =visual>
        ISA         mine
         > mine-angle-diff 180
         < mine-angle-diff 192
    ?finger-check>
        left-ring   free
==>
    +manual>
        ISA         delayed-punch
        hand        left
        finger      ring
)

(p hold-left-to-face-mine
    =goal>
        ISA         handle-mine
        state       "shoot-mine"
    =visual>
        ISA         mine
         >= mine-angle-diff 192
         < mine-angle-diff 348
    ?finger-check>
        left-ring   free
==>
    +manual>
        ISA         hold-key
        hand        left
        finger      ring
)

(p release-left-to-face-mine
    =goal>
        ISA         handle-mine
        state       "shoot-mine"
    =visual>
        ISA         mine
         >= mine-angle-diff 180
         < mine-angle-diff 192
    ?finger-check>
        left-ring   busy
==>
    +manual>
        ISA         release-key
        hand        left
        finger      ring
)

(p shoot-mine-over
    =goal>
        ISA         handle-mine
        state       "shoot-mine"
    =visual>
        ISA         mine
         > mine-angle-diff 348
         < mine-distance 180
    ?finger-check>
        left-thumb  free
==>
    +manual>
        ISA         delayed-punch
        hand        left
        finger      thumb
#|    +goal>
        ISA         fly-ship
        state       "look-for-ship"
    +visual>
        ISA         clear
    +visual-location>
        ISA         visual-location
        kind        ship  
|#
    =goal>
        state       "find-mine"
)

(p shoot-mine-under
    =goal>
        ISA         handle-mine
        state       "shoot-mine"
    =visual>
        ISA         mine
         < mine-angle-diff 12
         < mine-distance 180
    ?finger-check>
        left-thumb  free
==>
    +manual>
        ISA         delayed-punch
        hand        left
        finger      thumb
#|    +goal>
        ISA         fly-ship
        state       "look-for-ship"
    +visual>
        ISA         clear
    +visual-location>
        ISA         visual-location
        kind        ship    
|# 
    =goal>
        state       "find-mine"
)

(p mine-is-gone
    =goal>
        ISA          handle-mine
    =imaginal>
        ISA          symbol-record
        = mine-exist 0
==>
    +goal>
        ISA         fly-ship
        state       "look-for-ship"
    +visual>
        ISA         clear
    +visual-location>
        ISA         visual-location
        kind        ship     
)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;HANDLE BONUS SYMBOL PRODUCTIONS;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(p see-new-bonus-during-flight
     =goal>
         ISA         fly-ship
         state       "standard-flight-pattern"
     =imaginal>
         ISA         symbol-record
         = bonus-exist 1
         = symbol-attended "not-attended"
     ?finger-check>
         left-index  free
         left-middle free
         left-ring   free
==>
     +visual>
         ISA         clear ;stop tracking
     +visual-location>
         ISA         visual-location
         kind        bonus
     +goal>
         ISA         handle-bonus
         state       "find-bonus"
     =imaginal>
         last-goal   "ship"
         symbol-attended "attended" ;reset in device
     !safe-eval! (model-output "Noticed a symbol during flight")    
)

(p see-new-bonus-during-flight-release-thrust
     =goal>
         ISA         fly-ship
         state       "standard-flight-pattern"
     =imaginal>
         ISA         symbol-record
         = bonus-exist 1
         = symbol-attended "not-attended"
     ?finger-check>
         left-middle busy
==>
     +manual>
         ISA         release-key
         hand        left
         finger      middle
)

(p see-new-bonus-during-flight-release-right
     =goal>
         ISA         fly-ship
         state       "standard-flight-pattern"
     =imaginal>
         ISA         symbol-record
         = bonus-exist 1
         = symbol-attended "not-attended"
     ?finger-check>
         left-index  busy
==>
     +manual>
         ISA         release-key
         hand        left
         finger      index
)

(p see-new-bonus-during-flight-release-left
     =goal>
         ISA         fly-ship
         state       "standard-flight-pattern"
     =imaginal>
         ISA         symbol-record
         = bonus-exist 1
         = symbol-attended "not-attended"
     ?finger-check>
         left-ring   busy
==>
     +manual>
         ISA         release-key
         hand        left
         finger      ring
)

(p see-new-bonus-during-mine
     =goal>
         ISA         handle-mine
         state       "shoot-mine"
     =imaginal>
         ISA         symbol-record
         = bonus-exist 1
         = symbol-attended "not-attended"
     ?finger-check>
         left-index  free
         left-middle free
         left-ring   free
==>
     +visual>
         ISA         clear ;stop tracking
     +visual-location>
         ISA         visual-location
         kind        bonus
     +goal>
         ISA         handle-bonus
         state       "find-bonus"
     =imaginal>
         last-goal   "mine"
         symbol-attended "attended" ;reset in device
     !safe-eval! (model-output "Noticed a symbol during mine")  
)

(p see-new-bonus-during-mine-release-thrust
     =goal>
         ISA         handle-mine
         state       "shoot-mine"
     =imaginal>
         ISA         symbol-record
         = bonus-exist 1
         = symbol-attended "not-attended"
     ?finger-check>
         left-middle busy
==>
     +manual>
         ISA         release-key
         hand        left
         finger      middle
)

(p see-new-bonus-during-mine-release-right
     =goal>
         ISA         handle-mine
         state       "shoot-mine"
     =imaginal>
         ISA         symbol-record
         = bonus-exist 1
         = symbol-attended "not-attended"
     ?finger-check>
         left-index  busy
==>
     +manual>
         ISA         release-key
         hand        left
         finger      index
)

(p see-new-bonus-during-mine-release-left
     =goal>
         ISA         handle-mine
         state       "shoot-mine"
     =imaginal>
         ISA         symbol-record
         = bonus-exist 1
         = symbol-attended "not-attended"
     ?finger-check>
         left-ring   busy
==>
     +manual>
         ISA         release-key
         hand        left
         finger      ring
)

#|(p attend-new-bonus
    =goal>
        ISA         handle-bonus
        state       "find-bonus"
    =visual-location>
        ISA         visual-location
        kind        bonus
==>
    +visual>
        ISA         move-attention
        screen-pos  =visual-location
    =goal>
        state       "encode-bonus"
)|#

(p encode-non-bonus-not-expecting
    =goal>
        ISA         handle-bonus
        state       "find-bonus"
    =visual-location>
        ISA         visual-location
        kind        bonus
        value       =symbol
        - value     "$"
    =imaginal>
        ISA         symbol-record
        state       "not-expecting-bonus"
==>
    =goal>
        state       "return"
    !safe-eval! (model-output "Was ~A, not a bonus" =symbol)
)

(p encode-non-bonus-expecting
    =goal>
        ISA         handle-bonus
        state       "find-bonus"
    =visual-location>
        ISA         visual-location
        kind        bonus
        value       =symbol
        - value     "$"
    =imaginal>
        ISA         symbol-record
        state       "expecting-bonus"
==>
    =imaginal>
        state       "not-expecting-bonus"
    =goal>
        state       "return"
    !safe-eval! (model-output "Symbol was ~A, so longer expecting bonus" =symbol)
)

(p encode-bonus-not-expecting
    =goal>
        ISA         handle-bonus
        state       "find-bonus"
    =visual-location>
        ISA         visual-location
        kind        bonus
        value       =symbol
        value       "$"
    =imaginal>
        ISA         symbol-record
        state       "not-expecting-bonus"
==>
    =imaginal>
        state       "expecting-bonus"
    =goal>
        state       "return"
    !safe-eval! (model-output "Now expecting bonus")
)

(p encode-bonus-expecting
    =goal>
        ISA         handle-bonus
        state       "find-bonus"
    =visual-location>
        ISA         visual-location
        kind        bonus
        value       =symbol
        value       "$"
    =imaginal>
        ISA         symbol-record
        state       "expecting-bonus"
==>
    !safe-eval!     (model-output "Bonus available!")
    =goal>
        state       "determine-which-bonus"
    +visual-location>
        ISA         visual-location
        kind        vlcty
)

(p attend-vlcty
    =goal>
        ISA         handle-bonus
        state       "determine-which-bonus"
    =visual-location>
        ISA         visual-location
        kind        vlcty
==>
    +visual>
        ISA         move-attention
        screen-pos  =visual-location
)

(p vlcty-over-1750
    =goal>
        ISA         handle-bonus
        state       "determine-which-bonus"
    =visual>
        ISA         vlcty
        >= value    1750
    =imaginal>
        ISA         symbol-record
==>
    +manual>
        ISA         delayed-punch
        hand        right
        finger      ring ;close to end of game, take points
    =goal>
        state       "return"
    =imaginal>
        state       "not-expecting-bonus"
    !safe-eval! (model-output "Taking PNTS because it's close to the end")
)

(p vlcty-under-1750
    =goal>
        ISA         handle-bonus
        state       "determine-which-bonus"
    =visual>
        ISA         vlcty
        < value     1750
==>
    +visual-location>
        ISA         visual-location
        kind        shots
    !safe-eval! (model-output "Not close to end, need to base bonus decision on number of shots left")
)

(p attend-shots
    =goal>
        ISA         handle-bonus
        state       "determine-which-bonus"
    =visual-location>
        ISA         visual-location
        kind        shots
==>
    +visual>
        ISA         move-attention
        screen-pos  =visual-location
)

(p shots-under-50
    =goal>
        ISA         handle-bonus
        state       "determine-which-bonus"
    =visual>
        ISA         shots  
        <= value    50  
    =imaginal>
        ISA         symbol-record
==>
    +manual>
        ISA         delayed-punch
        hand        right
        finger      middle ;low on shots, need more missiles
    =goal>
        state       "return"
    =imaginal>
        state       "not-expecting-bonus"
    !safe-eval! (model-output "Low on missiles and not near end - taking SHOTS")
)

(p shots-over-50
    =goal>
        ISA         handle-bonus
        state       "determine-which-bonus"
    =visual>
        ISA         shots  
        > value     50  
    =imaginal>
        ISA         symbol-record
==>
    +manual>
        ISA         delayed-punch
        hand        right
        finger      ring ;have enough missiles, take points
    =goal>
        state       "return"
    =imaginal>
        state       "not-expecting-bonus"
    !safe-eval! (model-output "Have enough missiles - taking PNTS")
)

(p bonus-return-to-ship
    =goal>
        ISA          handle-bonus
        state        "return"
    =imaginal>
        ISA          symbol-record
        = last-goal  "ship"
==>
    +goal>
        ISA          fly-ship
        state        "look-for-ship"
    +visual>
        ISA          clear
    +visual-location>
        ISA          visual-location
        kind         ship
)

(p bonus-return-to-mine
    =goal>
        ISA          handle-bonus
        state        "return"
    =imaginal>
        ISA          symbol-record
        = last-goal  "mine"
==>
    +goal>
        ISA          handle-mine
        state        "find-mine"
    +visual>
        ISA          clear
    +visual-location>
        ISA          visual-location
        kind         mine
)

(p bonus-is-gone
    =goal>
        ISA          handle-bonus
    =imaginal>
        ISA          symbol-record
        = bonus-exist 0
==>
    +goal>
        ISA         fly-ship
        state       "look-for-ship"
    +visual>
        ISA         clear
    +visual-location>
        ISA         visual-location
        kind        ship     
)

;(spp mine-error-visloc :u 3)
;(spp mine-error-visual :u 3)
;(spp ship-error-visloc :u 3)
;(spp ship-error-visual :u 3)
(spp release-left-waiting-for-retrieval :u 3)
(spp release-right-waiting-for-retrieval :u 3)
(spp see-new-bonus-during-flight :u 3)
(spp see-new-bonus-during-mine :u 3)
(spp ship-destroyed-during-flight :u 5)
(spp ship-destroyed-during-mine :u 5)
(spp ship-destroyed-during-bonus :u 5)
(spp see-new-mine :u 3)
(spp mine-is-gone :u 4) ;if mine and ship are destroyed together, ship takes precedence

(set-visloc-default isa visual-location kind ship); :attended new) 

)