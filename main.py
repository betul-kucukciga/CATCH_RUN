import sys
import numpy
import moderngl
import pygame
import random
import os

def resource_path(relative_path):
    
    try:
        
        base_path = sys._MEIPASS
    except Exception:
        
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


pygame.init()
pygame.mixer.init()

bgm_path = resource_path(os.path.join( "assets", "background_sound.mp3"))
hit_path= resource_path(os.path.join( "assets", "danger_sound.wav"))
feed_path = resource_path(os.path.join( "assets", "feed_sound.wav"))



pygame.mixer.music.load(bgm_path)
pygame.mixer.music.set_volume(0.4) 
pygame.mixer.music.play(-1) 


bomb_sound = pygame.mixer.Sound(hit_path)
bomb_sound.set_volume(0.9)

feed_sound = pygame.mixer.Sound(feed_path)
feed_sound.set_volume(0.7)




pygame.display.set_mode((800,750), pygame.DOUBLEBUF | pygame.OPENGL)
ctx = moderngl.create_context()


v_shader='''
#version 330
layout (location= 0) in vec2 in_vert;
uniform vec2 u_offset;
uniform float u_scale; 

void main()
{
    gl_Position = vec4((in_vert * u_scale) + u_offset, 0.0, 1.0); 
}
'''

f_shader='''
#version 330
uniform vec3 u_color;
out vec4 f_color;
void main()
{
    f_color = vec4(u_color, 1.0);
}
'''

prog = ctx.program(vertex_shader = v_shader, fragment_shader = f_shader)

vertices = numpy.array([
    -0.15, -0.0866, 
    0.15, -0.0866, 
    0.0, 0.1732 
], dtype = 'f4')

vbo = ctx.buffer(vertices)
vao = ctx.vertex_array(prog, [(vbo, '2f', 'in_vert')]) 

obj_points = numpy.array([
    -0.06, 0.0,
    0.0, 0.0,
    -0.06, 0.06,
    -0.06, 0.06,
    0.0, 0.0,
    0.0, 0.06
], dtype = 'f4')


obj_vbo = ctx.buffer(obj_points)
obj_vao = ctx.vertex_array(prog, [(obj_vbo, '2f', 'in_vert' )]) 



ctx.point_size = 10.0
pos_x = 0.0
pos_y = 0.0
left_line = -1.0 - vertices[0]
right_line = 1.0 - vertices[2]
up_line = 1.0 - vertices[5]
down_line = -1.0 - vertices[3]

score = 0
game_duration= 60
game_start_time = pygame.time.get_ticks()
game_active = True
box = []             
last_obj_time = -2000
damage = False
damage_duration = 1000
damage_speed = 150
remainder_time = 3000

clock = pygame.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit() 
            sys.exit()

    ctx.clear(0.8, 0.7, 0.9, 1.0)

    elapsed_time = (pygame.time.get_ticks() - game_start_time) // 1000
    step = elapsed_time//10
    current_speed = min(0.04 + (step*0.005), 0.9)

    if (remainder_time > 0) and game_active:
        
            keys = pygame.key.get_pressed()
            if (keys[pygame.K_RIGHT] or keys[pygame.K_d]):
                    pos_x += current_speed
                    if pos_x > right_line:
                        pos_x = right_line        
                
            if (keys[pygame.K_LEFT] or keys[pygame.K_a]):
                    pos_x -= current_speed
                    if pos_x < left_line:
                        pos_x = left_line    

            if (keys[pygame.K_UP] or keys[pygame.K_w]):
                    pos_y += current_speed
                    if pos_y > up_line:
                        pos_y = up_line

            if (keys[pygame.K_DOWN] or keys[pygame.K_s]):
                    pos_y -= current_speed
                    if pos_y < down_line:
                        pos_y = down_line

            if keys[pygame.K_SPACE]:
                    pos_x = 0.0
                    pos_y = 0.0     


                    
            

            now_obj_time = pygame.time.get_ticks()
            rand_int_for_obj = random.randint(10, 20)
            bomb_probability = 0.25

            if (now_obj_time - last_obj_time) > 1800:
                
                box.clear()
                
                while len(box) == 0:
            
                    for i in range(rand_int_for_obj):
                            rand_x = random.uniform(left_line, right_line)
                            rand_y = random.uniform(down_line, up_line)
                            distance = ((rand_x - pos_x)**2 + (rand_y - pos_y)**2)**(1/2)
                            if (distance > 0.3):
                                new_obj = {'pos': [rand_x, rand_y]}

                                if (random.random() < bomb_probability):
                                    new_obj.update({'color': (0.0, 0.0, 0.0), 'size': (random.uniform(1.3, 1.8)), 'type': 'bomb'  })
                                else:
                                    new_obj.update({'color': (random.uniform(0.2, 1.0), random.uniform(0.2, 1.0), random.uniform(0.2, 1.0)), 'size': (random.uniform(0.8, 1.5)), 'type': 'feed'})
                        
                                box.append(new_obj)


                    last_obj_time = now_obj_time

                    
           

            x1 = vertices[0] + pos_x
            y1 = vertices[1] + pos_y
            x2 = vertices[2] + pos_x
            y2 = vertices[3] + pos_y
            x3 = vertices[4] + pos_x
            y3 = vertices[5] + pos_y
        
            triangle_area = abs(x1*(y2 - y3) + x2*(y3 - y1) + x3*(y1 - y2)) / 2.0
            copy_box = box[:]

                

            for obj in box:

                s_x = obj['pos'][0]
                s_y = obj['pos'][1]
                distance_squared = (x1 - s_x)**2 + (y1 - s_y)**2
                if distance_squared < 0.25: 
                        
                        
                        area_1 = abs(s_x*(y1 - y2) + x1*(y2 - s_y) + x2*(s_y - y1)) / 2.0
                        area_2 = abs(s_x*(y2 - y3) + x2*(y3 - s_y) + x3*(s_y - y2)) / 2.0
                        area_3 = abs(s_x*(y3 - y1) + x3*(y1 - s_y) + x1*(s_y - y3)) / 2.0
                        
                        total_area = area_1 + area_2 + area_3

                        
                        if total_area <= triangle_area + 0.003:
                            
                            
                            if obj['type'] == 'bomb':
                                score -= 3 
                                damage = True
                                damage_start_time = pygame.time.get_ticks()
                                bomb_sound.play()
                            else:
                                score += 1 
                                feed_sound.play()
                            
                            
                            box.remove(obj)  


            

            elapsed_time = (pygame.time.get_ticks() - game_start_time) // 1000           
            remainder_time = (game_duration - elapsed_time )  

            minute = remainder_time // 60
            sec = remainder_time % 60
            game_information = f"SKOR: {score}  |  KALAN SÜRE: {minute:02}:{sec:02}"
            pygame.display.set_caption(f"CATCH RUN! | {game_information}")
      
            if remainder_time <=0:
                game_active = False

    else:

        game_active = False
        pygame.mixer.music.stop()
        if score >= 100:
         message = "BABAYLA ZOR YARIŞIRLAR 😎 "
        elif (score >= 80) and (score < 100):
         message = "Atik, tetik ve çevik 👌"
        elif (score < 80) and (score >= 50):
         message = " Zirveye bir r tuşu uzaktayız 😁 "
        elif (score < 50) and (score >= 25):
         message = "Ümit vaat ediyorsun, bir deneme daha! 🤗" 
        elif (score >= 10) and (score < 25):
         message = "BABAYLA KOLAY YARIŞIRLAR GİBİ.. 😞"    
        elif (score < 10) and (score >= 0):
             message = "Isınma turları bittiyse asıl oyuna mı geçsek? 😊" 
        else:
             message = "Bence klavyen bozuktu, hadi tekrar! 😵‍💫"     

        pygame.display.set_caption(f"CATCH RUN! | OYUN BİTTİ!  SKORUNUZ: {score}   {message}  (tekrar oynamak için R tuşuna basınız)")

        key = pygame.key.get_pressed()
        if key[pygame.K_r]:
             score = 0
             game_duration= 60
             pos_x = 0.0
             pos_y = 0.0
             game_active = True
             box = []   
             damage = False
             last_obj_time = -2000
             remainder_time = 3000
             game_start_time = pygame.time.get_ticks()
             pygame.mixer.music.load(bgm_path)
             pygame.mixer.music.play(-1) 
             

       
    prog['u_scale'].value = 1.0
    prog['u_offset'].value = (pos_x, pos_y)

    if damage:
        decision = pygame.time.get_ticks() // damage_speed
        prog['u_color'].value = (1.0, 0.0, 0.0) if decision % 2 == 0 else (1.0, 1.0, 1.0)
        pygame.display.set_caption(f"CATCH RUN! | {game_information}  |  BOMBALARA DİKKAT ET!")
        if pygame.time.get_ticks() - damage_start_time > damage_duration:
            damage = False
    else:          

        prog['u_color'].value = (1.0, 0.4, 0.7) 

    vao.render(moderngl.TRIANGLES)         
        
    for obj in box:
            
        
        prog['u_color'].value = obj['color']
        prog['u_offset'].value = tuple(obj['pos'])
        prog['u_scale'].value = obj['size']
        obj_vao.render(moderngl.TRIANGLES)



    pygame.display.flip()
    pygame.time.wait(10)


    
    clock.tick(60)               
