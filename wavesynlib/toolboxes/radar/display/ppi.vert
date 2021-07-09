#version 420

attribute vec2 position;
out vec2 texcoord;

void main() {
    gl_Position = vec4(position, 0.0, 1.0 );
    texcoord = position;
}