"""Scary Game"""

import random
import arcade
import math
from pyglet.math import Vec2
from arcade.experimental.lights import Light, LightLayer

# --- Constants ---
CAMERA_SPEED = 0.1
MONSTER_RADIUS = 300
MOVE_SPEED = 3.5

SCREEN_WIDTH, SCREEN_HEIGHT = arcade.get_display_size()

class Monster(arcade.Sprite):
    def __init__(self, texture, scale, center_x, center_y, change_x, change_y):
        """ Constructor. """
        super().__init__(texture=texture, scale=scale)

        self.texture.filter = arcade.gl.NEAREST
        
        self.center_x = center_x
        self.center_y = center_y
        
        self.change_x = change_x
        self.change_y = change_y

        self.stationary_shot = False
        self.target_exists = False
        self.monster_speed = 3
        self.target_store = []

        self.delay = 0
        self.delay_max = 0

        # Change sprite direction

    def look_for_point(self):
        x = random.randrange(SCREEN_WIDTH)
        y = random.randrange(SCREEN_HEIGHT)
        return x, y
    
    def update(self):
        """Minecraft mob type movement. Find random [x,y] value, and once at the position, generate a new point to move to."""

        if self.stationary_shot == False and self.target_exists == False:
            if self.delay > 0:
                self.delay -= 1
                self.texture = arcade.load_texture("data/sprites/monster_sprite.png", x=0, y=0, width=32, height=32)
                return

            target_point = self.look_for_point()
            self.target_store = target_point
            self.target_exists = True

        if self.target_exists == True:
            dist = math.dist([self.center_x, self.center_y], self.target_store)
            if dist <= 10:
                self.change_x = 0
                self.change_y = 0
                self.target_exists = False

                self.delay_max = random.randint(30, 120)
                self.delay = self.delay_max
                return
            else:
                #Distance comes from subtraction -> (+): Positive Distance, (-): Negative Distance. Always (Target - Current)
                direction_x = (self.target_store[0] - self.center_x)
                direction_y = (self.target_store[1] - self.center_y)

                direction_x /= dist
                direction_y /= dist

                self.change_x = direction_x * self.monster_speed
                self.change_y = direction_y * self.monster_speed

                self.center_x += self.change_x
                self.center_y += self.change_y

        if self.change_x > 0:
            self.texture = arcade.load_texture("data/sprites/monster_sprite.png", x=64, y=0, width=32, height=32)
        elif self.change_x < 0:
            self.texture = arcade.load_texture("data/sprites/monster_sprite.png", x=32, y=0, width=32, height=32)


    def calc_radius(self, coor):
        monster_distance = math.sqrt((coor[0] - self.center_x)**2 + (coor[1] - self.center_y)**2)
        global enable_tracking, MONSTER_RADIUS, in_radius
        #print(monster_distance)
        if monster_distance  <= MONSTER_RADIUS:
            enable_tracking = True
            in_radius = True
        else:
            enable_tracking = False
            in_radius = False

    def get_distance(self, coor):
        dist = math.sqrt((coor[0] - self.center_x)**2 + (coor[1] - self.center_y)**2)
        return dist
        
class Generator(arcade.Sprite):
    def __init__(self, texture, scale, center_x, center_y):
        """Constructor"""
        super().__init__(texture=texture, scale=scale)
        self.texture.filter = arcade.gl.NEAREST
        
        #Location 
        self.center_x = center_x
        self.center_y = center_y
        self.gen_coor = [center_x, center_y]

        #Interactability States
        self.interactable = False
        self.generator_complete = False
        self.reach = 50

    def calc_interact(self, coor):
        generator_distance = math.dist(coor, self.gen_coor)
        if generator_distance  <= self.reach:
            self.interactable = True
        else:
            self.interactable = False

class MyGame(arcade.Window):
    """Our custom Window Class"""
       
    def __init__(self):
        """Initializer"""
        
        #Call the parent class initializer
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Scary Game", fullscreen=False, resizable=True, update_rate=1/60)
        
        self.set_location(100,100)
        
        # Variables that will hold sprite lists.
        self.player_list = None
        self.monster_list = None
        self.tree_list = None
        self.generator_list = None
        self.bullet_list = arcade.SpriteList()
        
        #Set up the player info
        self.player_sprite = None
        
        #Set up environment info
        self.level = 1
        self.sanity_color = arcade.color.GREEN
        
        #True / False
        self.inventory_open = False
        self.enable_tracking = False
        self.gun_on = False
        self.left_pressed = False
        self.right_pressed = False
        self.debug = False
        self.show_sanity = True
        global in_radius
        in_radius = True
        
        #Integers
        self.score = 0
        self.angle = 0
        self.tree_count = 10
        self.generator_count = 3
        self.sanity_initial = 100
        self.sanity = 0
        self.cam_zoom = .5
        self.rate_of_consumption = 0

        #Camera
        self.camera_sprites = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.camera_gui = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

        #Initate Light / Dark Ambience
        self.light_layer = LightLayer(self.width, self.height)
        self.player_light = Light(0, 0, 200, arcade.color.WHITE, mode="soft")
        self.light_layer.add(self.player_light)
        arcade.set_background_color(arcade.color.AMAZON)

        #Call Rate of Consumption function
        self.sanity_decrease()
        self.sanity = self.sanity_initial

        #Audio
        self.bgm = arcade.load_sound("data/audio/bgm/06.There_In_Spirit.wav")

        #BGM Player
        self.bgm_player = arcade.play_sound(self.bgm, volume=0.1, looping=True)


    def close(self):
        """Close the Window and stop background music"""
        super().close()

    def setup(self):
        """Set up the game and initialize the variables."""
        
        def coordinate_generate():
            x = random.randrange(SCREEN_WIDTH)
            y = random.randrange(SCREEN_HEIGHT)            
            generated_coordinate = [x, y]
            return generated_coordinate

        #Sprite Lists
        self.player_list = arcade.SpriteList()
        self.player_sprite = arcade.AnimatedTimeBasedSprite()
        texture = arcade.load_texture("data/sprites/sprite.png", x=0, y=0, width=32, height=32)
        anim = arcade.AnimationKeyframe(1,10,texture)
        self.player_sprite.frames.append(anim)
        
        #Set up the player
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 64
        self.player_list.append(self.player_sprite)
        self.inventory_dict = {
            "health_1": 0,
            "sanity_1": 0,
            "speed_1": 0,
            "health_2": 0,
            "sanity_2": 0,
            "speed_2": 0,}            
        
        #Set up the monster
        self.monster_list = arcade.SpriteList()
        monster_texture = arcade.load_texture("data/sprites/monster_sprite.png", x=0, y=0, width=32, height=32)
        monster = Monster(monster_texture, 2.5, 10, 10, 10, 10)
        self.monster_list.append(monster)
        
        #Set up trees
        self.tree_list = arcade.SpriteList()
        tree_texture = arcade.load_texture("data/sprites/terrain_sprite.png", x=0, y=32, width=32, height=32)
        for i in range(self.tree_count):
            tree_coor = coordinate_generate()

            tree = arcade.Sprite(scale=4)
            tree.texture = tree_texture
            tree.center_x = tree_coor[0]
            tree.center_y = tree_coor[1]

            self.tree_list.append(tree)


        #Set up generators
        self.generator_list = arcade.SpriteList()
        for i in range(self.generator_count):
            generator_coor = coordinate_generate()
            generator_texture_off = arcade.load_texture("data/sprites/terrain_sprite.png", x=0, y=0, width=32, height=32)
            generator = Generator(generator_texture_off, scale= 1.5, center_x= generator_coor[0], center_y= generator_coor[1])
            self.generator_list.append(generator)

    def sanity_decrease(self):
        decrease_factor = 1.3
        self.rate_of_consumption = 1 * decrease_factor**(self.level-1)
        return self.rate_of_consumption
    
    def on_uidraw(self):

        self.shapes = arcade.ShapeElementList()

        #Draw Inventory
        if self.inventory_open == True:
            arcade.draw_rectangle_filled(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, SCREEN_WIDTH/2, SCREEN_HEIGHT/2, arcade.color.BLACK)
            arcade.draw_text("Inventory:", SCREEN_WIDTH/4, SCREEN_HEIGHT/1.5, arcade.color.WHITE, 24)
            
            arcade.draw_text(f"Health Restore: T1: {self.inventory_dict['health_1']}, T2: {self.inventory_dict['health_2']}", SCREEN_WIDTH/4, SCREEN_HEIGHT/2, arcade.color.WHITE, 24)
            arcade.draw_text(f"Sanity Restore: T1: {self.inventory_dict['sanity_1']}, T2: {self.inventory_dict['sanity_2']}", SCREEN_WIDTH/4, SCREEN_HEIGHT/2.5, arcade.color.WHITE, 24)
            arcade.draw_text(f"Speed Restore: T1: {self.inventory_dict['speed_1']}, T2: {self.inventory_dict['speed_2']}", SCREEN_WIDTH/4, SCREEN_HEIGHT/3, arcade.color.WHITE, 24)
            
            arcade.draw_text(f"Score: {self.score}", 10, 10, arcade.color.WHITE, 24)
            arcade.draw_text(f"In Radius: {enable_tracking}", 10, 50, arcade.color.WHITE, 24)
            arcade.draw_text(f"Sanity: {self.sanity_initial}", 10, 90, arcade.color.WHITE, 24)

        #Draw Debug menu
        if self.debug == True:
            self.show_sanity = False
            arcade.draw_rectangle_filled(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, SCREEN_WIDTH, SCREEN_HEIGHT, arcade.color.BLACK)
            arcade.draw_text(f"Monster Radius: {MONSTER_RADIUS}", 10, SCREEN_HEIGHT-80, arcade.color.WHITE, 24)
            arcade.draw_text(f"Move Speed: {MOVE_SPEED}", 10, SCREEN_HEIGHT-110, arcade.color.WHITE, 24)
        
        #Draw Sanity
        if self.show_sanity == True:
            #Draw Sanity Meter Outline
            meter_width = SCREEN_WIDTH / 4
            meter_height = SCREEN_HEIGHT / 12
            margin = 10
            center_x = meter_width / 2 + margin
            center_y = meter_height / 2 + margin
            arcade.draw_rectangle_filled(center_x, center_y, meter_width, meter_height, arcade.color.BLACK)
            arcade.draw_rectangle_outline(center_x,center_y,meter_width, meter_height, arcade.color.WHITE, border_width=3)

            #Draw Sanity Meter
            sanity_ratio = self.sanity / self.sanity_initial
            fill_width = meter_width * sanity_ratio
            arcade.draw_rectangle_filled(center_x - (meter_width - fill_width) / 2, center_y, fill_width, meter_height - 4, self.sanity_color)
            arcade.draw_text(f"Sanity: {math.ceil(self.sanity)}", center_x - meter_width / 2, center_y + meter_height / 2 + 5, arcade.color.WHITE, 12)

        #Draw Alert bar
        if in_radius == True:
            for monster in self.monster_list:
                dist = monster.get_distance(PLAYER_POS)
                if dist <= 450:
                    # when dist = 200: opacity = 0
                    opacity = abs(dist - 450) / 450 
                    color1 = (136, 8, 8, int(255 * opacity))
                else:
                    color1 = (136, 8, 8, 0)
            color2 = (136, 8, 8, 0)
            points = (0, SCREEN_HEIGHT-200), (0, SCREEN_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT-200)
            colors = (color2, color1, color1, color2)
            rect = arcade.create_rectangle_filled_with_colors(points, colors)
            self.shapes.append(rect)
            self.shapes.draw()

    def on_draw(self):
        arcade.start_render()
        self.camera_sprites.use()
        self.camera_sprites.scale = self.cam_zoom
        # Draw world into the light layer
        with self.light_layer:

            arcade.draw_lrtb_rectangle_filled(
            0, self.width,
            self.height, 0,
            (54, 66, 40)
        )   
            self.tree_list.draw()
            self.generator_list.draw()
            self.monster_list.draw()
            self.player_list.draw()
            self.bullet_list.draw()

            if self.gun_on == True:
                x = 50 * math.sin(self.angle) + self.player_sprite.center_x
                y = 50 * math.cos(self.angle) + self.player_sprite.center_y
                arcade.draw_line(PLAYER_POS[0], PLAYER_POS[1], x, y, arcade.color.RED)

        # Draw the lighting effect over the world
        self.light_layer.draw()

        # Draw UI on top
        self.camera_gui.use()
        self.on_uidraw()

    def update(self, delta_time):
        """Movement and game logic"""
        
        #Call update on all sprites (Sprites dont do much in this example)
        self.player_list.update()
        self.player_list.update_animation()
        global PLAYER_POS, MONSTER_RADIUS, MOVE_SPEED
        PLAYER_POS = self.player_sprite.position
    

        #Sanity Decrease and Effects
        self.sanity -= 0.05 * (delta_time/2)
        if self.sanity <= 0:
            MONSTER_RADIUS = 1000
        elif self.sanity <= 20:
            MOVE_SPEED = 1
        elif self.sanity <= 30: #Distorted Vision
            self.sanity_color = arcade.color.RED
        elif self.sanity <= 60: #Monster Radius Increase & Audio Hallucinations
            self.sanity_color = arcade.color.YELLOW
        elif self.sanity <= 100: #Hallucinations 
            self.sanity_color = arcade.color.GREEN

        #Light Update
        self.player_light.position = (self.player_sprite.center_x,
                              self.player_sprite.center_y)
        
        #Player Movement Update
        if SCREEN_WIDTH-10 < PLAYER_POS[0]:
            self.player_sprite.change_x = 0
            
        elif 20 > PLAYER_POS[0]:
            self.player_sprite.change_x = 0
                
        if SCREEN_HEIGHT-10 < PLAYER_POS[1]:
            self.player_sprite.change_y = 0
                
        elif 20 > PLAYER_POS[1]:
            self.player_sprite.change_y = 0
        
        #Gun Update
        if self.left_pressed:
            self.angle -= 0.1
        elif self.right_pressed:
            self.angle += 0.1      
        self.bullet_list.update()  

        #Monster Update
        for monster in self.monster_list:
            monster.calc_radius(PLAYER_POS)        

        self.monster_list.update()
        monster_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.monster_list)
        for i in monster_hit_list:
            self.score+=1

        #Generator Update
        for generator in self.generator_list:
            generator.calc_interact(PLAYER_POS)

        self.scroll_to_player()
            
    def scroll_to_player(self):
        """
        Scroll the window to the player.

        if CAMERA_SPEED is 1, the camera will immediately move to the desired position.
        Anything between 0 and 1 will have the camera move to the location with a smoother
        pan.
        """

        position = Vec2(self.player_sprite.center_x - self.width / 2,
                        self.player_sprite.center_y - self.height / 2)
        self.camera_sprites.move_to(position, CAMERA_SPEED)

    def commands(self):
        command = input(": ")

        #Item Commands
        if command == "give_health1":
            self.inventory_dict["health_1"] += 1
        elif command == "give_health2":
            self.inventory_dict["health_2"] += 1
        elif command == "give_sanity1":
            self.inventory_dict["sanity_1"] += 1
        elif command == "give_sanity2":
            self.inventory_dict["sanity_2"] += 1
        elif command == "give_speed1":
            self.inventory_dict["speed_1"] += 1
        elif command == "give_speed2":
            self.inventory_dict["speed_2"] += 1
        
        #Variable Commands
        elif command == "sanity":
            self.sanity = int(input("What Sanity %? "))

        #Debug Menu
        elif command == "debug" and self.debug == True:
            self.debug = False
        elif command == "debug":
            self.debug = True
        
    def on_key_press(self, key, modifiers):
        """Check to see which key is being pressed and move the player in the
        appropriate direction"""
        
        #gun Angle
        if key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True    
        
        #Movement Keys (W, A, S, D)
        elif key == arcade.key.W:
            self.player_sprite.change_y = MOVE_SPEED
            self.player_sprite.frames.clear()
            for i in range(4):
                texture = arcade.load_texture("data/sprites/sprite.png", x = i * 32, y = 32, width = 32, height = 32)
                anim = arcade.AnimationKeyframe(i,250,texture)
                self.player_sprite.frames.append(anim)
                
        elif key == arcade.key.S:
            self.player_sprite.change_y = -MOVE_SPEED
            self.player_sprite.frames.clear()
            for i in range(4):
                texture = arcade.load_texture("data/sprites/sprite.png", x = i * 32, y = 0, width = 32, height = 32)
                anim = arcade.AnimationKeyframe(i,250,texture)
                self.player_sprite.frames.append(anim)
                
        elif key == arcade.key.D:
            self.player_sprite.change_x = MOVE_SPEED
            self.player_sprite.frames.clear()
            for i in range(4):
                texture = arcade.load_texture("data/sprites/sprite.png", x = i * 32, y = 96, width = 32, height = 32)
                anim = arcade.AnimationKeyframe(i,250,texture)
                self.player_sprite.frames.append(anim)
                
        elif key == arcade.key.A:
            self.player_sprite.change_x = -MOVE_SPEED
            self.player_sprite.frames.clear()
            for i in range(4):
                texture = arcade.load_texture("data/sprites/sprite.png", x = i * 32, y = 64, width = 32, height = 32)
                anim = arcade.AnimationKeyframe(i,250,texture)
                self.player_sprite.frames.append(anim)
        
        #Generator Interactivity Key
        elif key == arcade.key.E:
            for gen in self.generator_list:
                if gen.interactable == True and gen.generator_complete == False:
                    gen.generator_complete = True
                    gen.texture = arcade.load_texture("data/sprites/terrain_sprite.png", x=32, y=0, width=32, height=32)

        #Inventory & gun Toggle
        elif key == arcade.key.K:
            if self.inventory_open == False:
                self.inventory_open = True
                print("Inventory Open")
            else:
                self.inventory_open = False
                print("Inventory Close")
                
        elif key == arcade.key.L:
            if self.gun_on == False:
                self.gun_on = True
                print("gun On")
            else:
                self.gun_on = False
                print("gun Off")        
        
        #Shooting
        elif key == arcade.key.SPACE:
            bullet_sprite = arcade.Sprite(
                ":resources:images/space_shooter/laserBlue01.png", scale=1
            )
            # Set starting position at player
            bullet_sprite.center_x = self.player_sprite.center_x
            bullet_sprite.center_y = self.player_sprite.center_y

            # Set velocity using angle (no player coordinates here)
            bullet_speed = 10
            bullet_sprite.change_x = bullet_speed * math.sin(self.angle)
            bullet_sprite.change_y = bullet_speed * math.cos(self.angle)

            # Add to bullet list
            self.bullet_list.append(bullet_sprite)

        #Command Prompt
        elif key == arcade.key.T:
            self.commands()
             
    def on_key_release(self, key, modifiers):
        """Check to see which key is being pressed and move the player in the
        appropriate direction"""
        
        #gun Angle
        if key == arcade.key.LEFT:
            self.left_pressed = False
        
        elif key == arcade.key.RIGHT:
            self.right_pressed = False
        
        if key == arcade.key.W:
            self.player_sprite.change_y = 0
            self.player_sprite.frames.clear()
            for i in range(4):
                texture = arcade.load_texture("data/sprites/sprite.png", x = 0, y = 0, width = 32, height = 32)
                anim = arcade.AnimationKeyframe(i,10,texture)
                self.player_sprite.frames.append(anim)            
                        
        elif key == arcade.key.S:
            self.player_sprite.change_y = 0
            self.player_sprite.frames.clear()
            for i in range(4):
                texture = arcade.load_texture("data/sprites/sprite.png", x = 0, y = 0, width = 32, height = 32)
                anim = arcade.AnimationKeyframe(i,10,texture)
                self.player_sprite.frames.append(anim)            
                        
        elif key == arcade.key.D:
            self.player_sprite.change_x = 0
            self.player_sprite.frames.clear()
            for i in range(4):
                texture = arcade.load_texture("data/sprites/sprite.png", x = 0, y = 96, width = 32, height = 32)
                anim = arcade.AnimationKeyframe(i,10,texture)
                self.player_sprite.frames.append(anim)
                
        elif key == arcade.key.A:
            self.player_sprite.change_x = 0
            self.player_sprite.frames.clear()
            for i in range(4):
                texture = arcade.load_texture("data/sprites/sprite.png", x = 0, y = 64, width = 32, height = 32)
                anim = arcade.AnimationKeyframe(i,10,texture)
                self.player_sprite.frames.append(anim)            
            

def main():
    """Main Method"""
    window = MyGame()
    window.setup()
    arcade.run()
    
if __name__ == "__main__":
    main()