#version 330

in vec2 texCoord;
in vec3 vertex_color;
in vec3 FragPos;
in vec3 Normal;
in vec3 LightPos;

out vec4 fragColor;

uniform int ShadingType; // 0 = gouraud, 1 = phong
//uniform int LightMode;
uniform vec3 viewPos;

struct Light
{
    float angle;
    vec3 position;
    vec3 diffuse;
};
uniform Light light;

uniform int isEye;

struct Offset
{
    float x;
    float y;
};
uniform Offset eyeOffset;

struct Material
{
    vec3 Ka;
    vec3 Kd;
    vec3 Ks;
    float shininess;
};
uniform Material material;

vec3 result;
//float constant;
//float linear;
//float quadratic;
//float distance;
//float attenuation;
//float theta;

// [TODO] passing texture from main.cpp
// Hint: sampler2D

uniform sampler2D diffuseTexture;

// [TODO] sampleing from texture
// Hint: texture

void main()
{
    if (ShadingType == 0)
    {
		fragColor = texture(diffuseTexture, texCoord) * vec4(vertex_color, 1.0);
    }
    else if (ShadingType == 1)
    {
    // ambient
		vec3 ambient = vec3(0.15f, 0.15f, 0.15f) * material.Ka;

    // diffuse
		vec3 norm = normalize(Normal);
		vec3 lightDir = normalize(-vec3(-1.0f, -1.0f, -1.0f));
		float diff = max(dot(norm, lightDir), 0.0);
		vec3 diffuse = light.diffuse * material.Kd * diff;

    // specular
		vec3 lightspecular = light.diffuse;
		vec3 viewDir = normalize(viewPos - FragPos);
		vec3 halfwayDir = normalize(lightDir + viewDir);
		float spec = pow(max(dot(norm, halfwayDir), 0.0), material.shininess);
		vec3 specular = lightspecular * (spec * material.Ks);

		result = ambient + diffuse + specular;
		fragColor = texture(diffuseTexture, texCoord) * vec4(result, 1.0f);
    }
}