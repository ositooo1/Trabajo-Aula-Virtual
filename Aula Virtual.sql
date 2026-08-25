CREATE TABLE `roles` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `nombre` varchar(30) UNIQUE COMMENT 'admin, docente, estudiante'
);

CREATE TABLE `usuarios` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `rol_id` int,
  `nombre` varchar(100),
  `apellido` varchar(100),
  `email` varchar(150) UNIQUE,
  `password_hash` varchar(255),
  `activo` boolean DEFAULT true,
  `creado_en` datetime DEFAULT (now())
);

CREATE TABLE `ciclos_lectivos` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `nombre` varchar(50) COMMENT 'ej: 2026 - 1er Cuatrimestre',
  `fecha_inicio` date,
  `fecha_fin` date
);

CREATE TABLE `cursos` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `nombre` varchar(150),
  `descripcion` text,
  `ciclo_lectivo_id` int,
  `creado_por` int,
  `activo` boolean DEFAULT true,
  `creado_en` datetime DEFAULT (now())
);

CREATE TABLE `docentes_cursos` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `curso_id` int,
  `docente_id` int,
  `asignado_en` datetime DEFAULT (now())
);

CREATE TABLE `inscripciones` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `curso_id` int,
  `estudiante_id` int,
  `inscrito_en` datetime DEFAULT (now())
);

CREATE TABLE `materiales` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `docente_id` int COMMENT 'docente dueño del material',
  `titulo` varchar(200),
  `descripcion` text,
  `contenido` text COMMENT 'archivo, link o contenido del material',
  `creado_en` datetime DEFAULT (now())
);

CREATE TABLE `materiales_publicados` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `curso_id` int,
  `material_id` int,
  `publicado_en` datetime DEFAULT (now())
);

CREATE TABLE `formatos_evaluacion` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `docente_id` int COMMENT 'docente dueño del formato',
  `titulo` varchar(200),
  `descripcion` text,
  `creado_en` datetime DEFAULT (now())
);

CREATE TABLE `preguntas` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `formato_id` int,
  `enunciado` text,
  `puntaje` decimal(5,2) DEFAULT 1,
  `orden` int DEFAULT 0
);

CREATE TABLE `evaluaciones_curso` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `curso_id` int,
  `formato_id` int,
  `fecha_limite` datetime,
  `intentos_maximos` int DEFAULT 1,
  `es_recuperatorio` boolean DEFAULT false,
  `evaluacion_padre_id` int COMMENT 'null salvo que sea recuperatorio',
  `creado_en` datetime DEFAULT (now())
);

CREATE TABLE `intentos` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `evaluacion_curso_id` int,
  `estudiante_id` int,
  `numero_intento` int DEFAULT 1,
  `entregado_en` datetime
);

CREATE TABLE `respuestas` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `intento_id` int,
  `pregunta_id` int,
  `respuesta_texto` text
);

CREATE TABLE `calificaciones` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `intento_id` int UNIQUE,
  `nota` decimal(5,2),
  `calificado_por` int,
  `calificado_en` datetime DEFAULT (now())
);

CREATE UNIQUE INDEX `docentes_cursos_index_0` ON `docentes_cursos` (`curso_id`, `docente_id`);

CREATE UNIQUE INDEX `inscripciones_index_1` ON `inscripciones` (`curso_id`, `estudiante_id`);

ALTER TABLE `usuarios` ADD FOREIGN KEY (`rol_id`) REFERENCES `roles` (`id`);

ALTER TABLE `cursos` ADD FOREIGN KEY (`ciclo_lectivo_id`) REFERENCES `ciclos_lectivos` (`id`);

ALTER TABLE `cursos` ADD FOREIGN KEY (`creado_por`) REFERENCES `usuarios` (`id`);

ALTER TABLE `docentes_cursos` ADD FOREIGN KEY (`curso_id`) REFERENCES `cursos` (`id`);

ALTER TABLE `docentes_cursos` ADD FOREIGN KEY (`docente_id`) REFERENCES `usuarios` (`id`);

ALTER TABLE `inscripciones` ADD FOREIGN KEY (`curso_id`) REFERENCES `cursos` (`id`);

ALTER TABLE `inscripciones` ADD FOREIGN KEY (`estudiante_id`) REFERENCES `usuarios` (`id`);

ALTER TABLE `materiales` ADD FOREIGN KEY (`docente_id`) REFERENCES `usuarios` (`id`);

ALTER TABLE `materiales_publicados` ADD FOREIGN KEY (`curso_id`) REFERENCES `cursos` (`id`);

ALTER TABLE `materiales_publicados` ADD FOREIGN KEY (`material_id`) REFERENCES `materiales` (`id`);

ALTER TABLE `formatos_evaluacion` ADD FOREIGN KEY (`docente_id`) REFERENCES `usuarios` (`id`);

ALTER TABLE `preguntas` ADD FOREIGN KEY (`formato_id`) REFERENCES `formatos_evaluacion` (`id`);

ALTER TABLE `evaluaciones_curso` ADD FOREIGN KEY (`curso_id`) REFERENCES `cursos` (`id`);

ALTER TABLE `evaluaciones_curso` ADD FOREIGN KEY (`formato_id`) REFERENCES `formatos_evaluacion` (`id`);

ALTER TABLE `evaluaciones_curso` ADD FOREIGN KEY (`evaluacion_padre_id`) REFERENCES `evaluaciones_curso` (`id`);

ALTER TABLE `intentos` ADD FOREIGN KEY (`evaluacion_curso_id`) REFERENCES `evaluaciones_curso` (`id`);

ALTER TABLE `intentos` ADD FOREIGN KEY (`estudiante_id`) REFERENCES `usuarios` (`id`);

ALTER TABLE `respuestas` ADD FOREIGN KEY (`intento_id`) REFERENCES `intentos` (`id`);

ALTER TABLE `respuestas` ADD FOREIGN KEY (`pregunta_id`) REFERENCES `preguntas` (`id`);

ALTER TABLE `calificaciones` ADD FOREIGN KEY (`intento_id`) REFERENCES `intentos` (`id`);

ALTER TABLE `calificaciones` ADD FOREIGN KEY (`calificado_por`) REFERENCES `usuarios` (`id`);
