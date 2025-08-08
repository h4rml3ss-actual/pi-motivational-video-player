// bloom.glsl: Simple bloom shader

#version 120
uniform sampler2D texture;
varying vec2 texture_coords;

void main()
{
    vec4 sum = vec4(0.0);
    float offset = 1.0 / 512.0;
    for (int x = -2; x <= 2; x++) {
        for (int y = -2; y <= 2; y++) {
            sum += texture2D(texture, texture_coords + vec2(x, y) * offset);
        }
    }
    gl_FragColor = sum / 25.0;
}
