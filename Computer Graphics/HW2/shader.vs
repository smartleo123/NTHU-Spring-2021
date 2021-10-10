#version 330 core
# define M_PI 3.1415926

layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aColor;
layout (location = 2) in vec3 aNormal;

out vec3 vertex_color;
out vec3 vertex_normal;
out vec3 vertex_pos;


//struct Light  {
//  float angle;
//  vec3 position; 
//  vec3 diffuse;     
//};

//struct Material  {
//  vec3 Ka;            
//  vec3 Kd;          
//  vec3 Ks;           
//  float shininess;  
//};

uniform mat4 mvp;
uniform mat4 mv;

uniform vec3 ka;
uniform vec3 kd;
uniform vec3 ks;
uniform vec3 light_dir;
uniform vec3 light_pos;
uniform vec3 intensity;
uniform int cur_light_mode;
uniform int shininess;
uniform int angle;
uniform int shade_mode;

void main()
{
	// [TODO]
	gl_Position = mvp * vec4(aPos.x, aPos.y, aPos.z, 1.0);

//phong_model
	vec4 pos = mv * vec4(aPos.x, aPos.y, aPos.z, 1.0);
	vertex_pos = vec3(pos.x, pos.y, pos.z);

	vec4 normal = transpose(inverse(mv)) * vec4(aNormal.x, aNormal.y, aNormal.z, 0.0);
	vertex_normal = vec3(normal.x, normal.y, normal.z);

//gouraud
	vec3 result;

//ambient
	vec3 ambient_strength = vec3(0.15f, 0.15f, 0.15f);
	vec3 La = ambient_strength;
	
//diffuse
	vec3 Ld = intensity;
	vec3 norm = normalize(vertex_normal);
	
	vec3 lightDir;
	
	switch(cur_light_mode){
		case 0:
			lightDir = normalize(light_pos);
			break;
		case 1:
			lightDir = normalize(light_pos - vertex_pos);
			break;
		case 2:
			lightDir = normalize(light_pos - vertex_pos);
			break;
	}
	float diff = max(dot(norm, lightDir), 0.0);

//specular
	vec3 Ls = intensity;

	//half way vector
	vec3 reflectDir;
	if (cur_light_mode == 0) 
		reflectDir = normalize(light_pos - vertex_pos);
	else if (cur_light_mode == 1 || cur_light_mode == 2) 
		reflectDir = normalize((light_pos - vertex_pos) + vertex_pos);

	//vec3 vertexDir = -normalize(vertex_pos);
	//reflectDir = normalize(vertexDir + lightDir);

	float spec = pow(max(dot(reflectDir, norm), 0.0), shininess);

//attenuation
	float attenuation_d;
	float attenuation_s;
	if (cur_light_mode == 1){
		float distance = length(light_pos - vertex_pos);
		attenuation_d = 1.0 / (0.01 + 0.8 * distance + 0.1 * distance * distance);
	}
	else if (cur_light_mode == 2){
		float distance = length(light_pos - vertex_pos);
		attenuation_s = 1.0 / (0.05 + 0.3 * distance + 0.6 * distance * distance);
	}

//result
	switch(cur_light_mode){
		case 0:
			result = La * ka + Ld * kd * diff  + Ls * ks * spec; //directional light mode
			break;
		case 1:
			result = attenuation_d * (La * ka + Ld * kd * diff +  Ls * ks * spec); //point light mode
			break;
		case 2:
			float cosine = dot(vertex_pos - light_pos, light_dir) / (length(vertex_pos - light_pos) * length(light_dir)); //spot light mode
			if (cosine <= cos(angle * M_PI / 180)){
				result = La * ka;
			}
			else if (cosine > cos(angle * M_PI / 180)){
				float spot_effect = pow(max(dot(normalize(vertex_pos - light_pos), normalize(light_dir)), 0), 50);
				result = spot_effect * (La * ka + Ld * kd * diff + Ls * ks * spec);
			}
	}

    vertex_color = result;
}
