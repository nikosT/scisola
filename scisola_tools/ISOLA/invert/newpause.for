       character *8 a
       
       a="message1"
       
       call newpause(a)
       
       stop
       end
       
       subroutine newpause(a)
       character *8 a
       write(*,*) a
       read(*,*)
       end