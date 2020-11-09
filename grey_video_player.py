#!/usr/bin/env python3

import cv2,threading,queue

#global queues
extract_queue = queue.Queue()
grey_converted_queue = queue.Queue()

global frame_queue
frame_queue = True # global flag

max_buffer = 10 # max frames to load

#global semaphpores
semaphore_empty = threading.Semaphore(max_buffer)
semaphore_full = threading.Semaphore(0)

lock_thread = threading.Lock()

def main_grey_player():  
    file_name = 'clip.mp4' # clip
    frame_delay = 42 

    # initalize threads
    extraction_thread = extract_frames(file_name, extract_queue) 
    converstion_thread = grey_frames(extract_queue, grey_converted_queue)
    display_thread = display_frames(grey_converted_queue, frame_delay)

    # start threads
    extraction_thread.start()
    converstion_thread.start()
    display_thread.start()

class extract_frames(threading.Thread):
    def __init__(self,file_name, extract_queue):
        threading.Thread.__init__(self)
        self.file_name = file_name
        self.extract_queue = extract_queue

    def run(self):
        count = 0
        global frame_queue 
        print("IN extract")
        # open the video clip
        video_capture = cv2.VideoCapture(self.file_name)
        # read the first frame
        success,frame = video_capture.read()
        
        while success:

            #insert frame into queue
            semaphore_empty.acquire()
            lock_thread.acquire()
            self.extract_queue.put(frame)
            lock_thread.release()
            semaphore_full.release()

            #read next frame
            success,frame = video_capture.read()
            #print(f'Extracting frame {count}')
            count += 1
        #update global flag
        success,frame = video_capture.read()
        frame_queue = success # global flag
        print("Extraction Complete")
    
class grey_frames(threading.Thread):
    def __init__(self,extract_queue, grey_converted_queue):
        threading.Thread.__init__(self)
        self.grey_converted_queue = grey_converted_queue
        self.extract_queue = extract_queue

    def run(self):
        count = 0
        global frame_queue
        print("IN converting")
         
        while frame_queue:
            #print(f'in converstion {frame_queue}')
            if not extract_queue.empty(): 

                #extract frame from queue
                semaphore_full.acquire()
                lock_thread.acquire()
                frame = extract_queue.get()
                lock_thread.release()
                semaphore_empty.release()
                
                #print(f'Converting frame {count}')
                #convert extracted frame to grey
                grayscaleFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                count += 1

                #insert grey converted frame into queue
                semaphore_empty.acquire()
                lock_thread.acquire()
                grey_converted_queue.put(grayscaleFrame)
                lock_thread.release()
                semaphore_full.release()
                
        print("Conversion Complete")
    
class display_frames(threading.Thread):
    def __init__(self, grey_converted_queue, frame_delay):
        threading.Thread.__init__(self)
        self.grey_converted_queue = grey_converted_queue
        self.frame_delay = frame_delay
    
    def run(self):
        count = 0
        global frame_queue
        print("IN display")
        
        while frame_queue:
            if not grey_converted_queue.empty():

                #extract grey frame from queue
                semaphore_full.acquire()
                lock_thread.acquire()
                frame = grey_converted_queue.get()
                lock_thread.release()
                semaphore_empty.release()
            
                #print(f'Displaying frame {count}')        

                #display the frame in a window called "video" and wait 42ms
                cv2.imshow('Video', frame)
                
                #before displaying the next frame
                if cv2.waitKey(self.frame_delay) and 0xFF == ord("q"):
                    break
                count += 1

        print("Displaying Complete")
        cv2.destroyAllWindows()    
    
if __name__ == "__main__":
    main_grey_player()
