// crt-geom.glsl: CRT geometry warp shader

#version 120
uniform sampler2D texture;
varying vec2 texture_coords;
uniform float curvature = 0.1;

void main()
{
    vec2 uv = texture_coords - vec2(0.5);
    float dist = dot(uv, uv);
    vec2 warped = uv + uv * dist * curvature;
    warped += vec2(0.5);
    if (warped.x < 0.0 || warped.x > 1.0 || warped.y < 0.0 || warped.y > 1.0) {
        gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
    } else {
        gl_FragColor = texture2D(texture, warped);
    }
}
