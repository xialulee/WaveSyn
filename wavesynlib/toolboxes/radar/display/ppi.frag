#version 420

#define PI {{pi}}
#define TWO_PI (2*PI)

uniform sampler2D image;
uniform float current_angle;
uniform float start_angle;
uniform float stop_angle;
uniform float angle_interval;
in vec2 texcoord;
out vec3 frag_color;

{{hit_circle}}
{{hit_line}}



bool is_angle_valid(inout float angle, float start_angle, float stop_angle) {
    if (start_angle <= angle && angle <= stop_angle) {
        return true;
    } 

    float new_angle = TWO_PI + angle;
    if (start_angle <= new_angle && new_angle <= stop_angle) {
        angle = new_angle;
        return true;
    }

    return false;
}



void main() {
    float angle;    
    float len;
    float hit;

    for (int i=1; i<=3; ++i) {    
        hit = hit_circle(texcoord, 1.0/3.0*i, 0.005);
        if (hit>0) break;
    }
    
    if (hit == 0.0) {
        hit = hit_line(texcoord, vec2(-1.0, 0.0), vec2(1.0, 0.0), 0.005);
        hit += hit_line(texcoord, vec2(0.0, -1.0), vec2(0.0, 1.0), 0.005);
    }
        
    vec3 color = vec3(0.0, 0.0, 0.0);        
    float range = length(texcoord);
    if (range<=1) {
        angle = atan(texcoord.x, texcoord.y);
        if (is_angle_valid(angle, start_angle, stop_angle)) {
            /*
            color.g = (texture(image, vec2(angle / TWO_PI, len)) 
                * max(1 - mod(angle+current_angle, TWO_PI) / TWO_PI * 3, 0)).g;
            */
            color.g = (texture(
                image, 
                vec2(
                    range, 
                    (angle - start_angle)/angle_interval))).g;
            color.rb = vec2(0.0, 0.0);
        }
    }
            
    if (hit>0.0) {
        frag_color = mix(color, vec3(0.0, 1.0, 0.0)*hit*0.5, 0.35);
    } else {
        frag_color = color;
    }
}