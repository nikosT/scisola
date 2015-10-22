      program norm15

      dimension x1(8192,21,3)
      dimension x2(8192,21,3)
      dimension x3(8192,21,3)

c     CHARACTER *12 filename
      CHARACTER *5 statname(21)
      CHARACTER *17 statfil1,statfil2,statfil3


      open(99,file='inpinv.dat')
      open(100,file='allstat.dat')
      open(101,file='inv4.dat')   ! final varred from all stats (no weights)
                                  ! incl stations removed from inversion

      do i=1,3
      read(99,*)
      enddo
      read(99,*) dt

      ir=1
  10  read(100,*,end=20) statname(ir),dum,dum,dum,dum
      ir=ir+1
      if(ir.gt.21) goto 20
      goto 10
  20  continue
      nr=ir-1
      write(*,*) 'nr=', nr
c     if(nr.gt.21) then
c     write(*,*) 'TOO MANY STATIONS !!!!!'
c     stop
c     endif



      ntim=8192

c
c     READING SEISMOGRAMS (=DATA)
c


      do ir=1,nr         
        nfile=1000+1*ir
        statfil1=trim(statname(ir))//'fil.dat'
        open(nfile,file=statfil1)
        do itim=1,ntim     
        read(nfile,'(4(1x,e12.6))') time,
     *      x1(itim,ir,1),x1(itim,ir,2),x1(itim,ir,3)
        enddo
      close(nfile) 
      enddo


      do ir=1,nr         
       nfile=2000+1*ir
       statfil2=trim(statname(ir))//'res.dat'
       open(nfile,file=statfil2)
        do itim=1,ntim   
        read(nfile,'(4(1x,e12.6))') time,
     *      x2(itim,ir,1),x2(itim,ir,2),x2(itim,ir,3)
        enddo
	close(nfile)
      enddo

      do icom=1,3        
       do ir=1,nr        
        do itim=1,ntim   
        x3(itim,ir,icom)=x1(itim,ir,icom)-x2(itim,ir,icom)
        enddo
       enddo
      enddo


      anorm1=0.
      do icom=1,3        
       do ir=1,nr        
        do itim=1,ntim   
        anorm1=anorm1 +x1(itim,ir,icom)*x1(itim,ir,icom)
        enddo
       enddo
      enddo
      anorm1=anorm1*dt


      anorm2=0.
      do icom=1,3        
       do ir=1,nr        
        do itim=1,ntim   
        anorm2=anorm2 +x2(itim,ir,icom)*x2(itim,ir,icom)
        enddo
       enddo
      enddo
      anorm2=anorm2*dt        !sum of residuals squared


      anorm3=0.
      do icom=1,3        
       do ir=1,nr        
        do itim=1,ntim   
        anorm3=anorm3 +x3(itim,ir,icom)*x3(itim,ir,icom)
        enddo
       enddo
      enddo
      anorm3=anorm3*dt

      varred= 1. - anorm2/anorm1		! variance reduction

	numbd=(3*nr*ntim) ! number of data

	postvar=anorm2/float(3*nr*ntim)  ! a posteriori data variance


      do ir=1,nr         
       nfile=3000+1*ir
       statfil3=trim(statname(ir))//'syn.dat'
       open(nfile,file=statfil3)
        do itim=1,ntim   
        time=float(itim-1)*dt
        write(nfile,'(4(1x,e12.6))') time,
     *      x3(itim,ir,1),x3(itim,ir,2),x3(itim,ir,3)
        enddo
	close(nfile)
      enddo




      write(101,*) anorm2,anorm1,varred,postvar,numbd

      write(101,*) 
      write(101,*) 'sum of residuals squared='
      write(101,*)  anorm2

      write(101,*) 
      write(101,*) 'sum of data squared='
      write(101,*)  anorm1

      write(*,*) 
      write(*,*) 'variance reduction from ALL stations'
      write(*,*) '(including those NOT used in the inversion):'      
      write(*,*) 'varred=', varred

      write(101,*)
      write(101,*) 'variance reduction from ALL stations'
      write(101,*) '(including those NOT used in the inversion):'      
      write(101,*) 'varred='
      write(101,*)  varred

	
      write(101,*)
      write(*,*) 'a posteriori data variance from ALL stations'
      write(*,*) '(including those NOT used in the inversion):'      
      write(*,*) 'postvar=', postvar

      write(101,*) 'a posteriori data variance from ALL stations'
      write(101,*) '(including those NOT used in the inversion):'      
      write(101,*) 'postvar='
      write(101,*)  postvar

      write(101,*) 
      write(101,*) 'Number of data =(3*nr*ntim)='
 	write(101,*)  numbd

c      write(101,*) 
c      write(101,*) 'Chi^2 = (sum of residuals squared) /(data variance)'
c  	write(101,*) 'Sometimes it is assumed that (data variance) = postvar'

      stop
      end

 