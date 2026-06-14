INSERT INTO usuarios
(
    nombre,
    usuario,
    correo,
    password_hash,
    rol
)
VALUES
(
    'Administrador Principal',
    'IA1-User',
    'admin@smartbot.com',
    'CAMBIAR_POR_HASH_REAL',
    'admin'
);


INSERT INTO categorias
(nombre, descripcion)
VALUES
('Inscripciones', 'Procesos de inscripción'),
('Pagos', 'Información sobre pagos'),
('Cursos', 'Información académica'),
('Soporte', 'Ayuda técnica');


INSERT INTO preguntas_frecuentes
(pregunta,respuesta,categoria_id)
VALUES

(
'¿Cómo puedo inscribirme?',
'Debe ingresar al portal institucional y completar el formulario de inscripción.',
1
),

(
'¿Cuál es la fecha límite de inscripción?',
'La fecha límite es publicada cada ciclo académico en el calendario oficial.',
1
),

(
'¿Puedo modificar mis datos después de inscribirme?',
'Sí, desde el portal de estudiantes puede actualizar su información personal.',
1
),

(
'¿Qué documentos necesito para inscribirme?',
'Debe presentar documento de identificación y comprobante de pago.',
1
),

(
'¿Puedo cancelar una inscripción?',
'Sí, siempre que la solicitud se realice dentro de los plazos establecidos.',
1
);


INSERT INTO preguntas_frecuentes
(pregunta,respuesta,categoria_id)
VALUES

(
'¿Cuáles son los métodos de pago disponibles?',
'Puede pagar mediante transferencia bancaria o tarjeta.',
2
),

(
'¿Dónde puedo descargar mi comprobante de pago?',
'Puede descargarlo desde el portal de estudiantes.',
2
),

(
'¿Qué hago si mi pago no aparece registrado?',
'Debe comunicarse con soporte y adjuntar el comprobante correspondiente.',
2
),

(
'¿Puedo solicitar reembolso?',
'Los reembolsos se evalúan según las políticas institucionales vigentes.',
2
),

(
'¿Existen recargos por pago tardío?',
'Sí, los pagos realizados fuera de fecha pueden generar recargos.',
2
);


INSERT INTO preguntas_frecuentes
(pregunta,respuesta,categoria_id)
VALUES

(
'¿Cómo consulto mis cursos asignados?',
'Puede revisar sus cursos desde el portal académico.',
3
),

(
'¿Puedo cambiar de curso?',
'Los cambios dependen de la disponibilidad y autorización correspondiente.',
3
),

(
'¿Dónde encuentro el programa del curso?',
'Cada curso publica su programa en la plataforma académica.',
3
),

(
'¿Qué hago si no aparezco en la lista del curso?',
'Debe comunicarse con coordinación académica para verificar su inscripción.',
3
),

(
'¿Cómo consulto mis calificaciones?',
'Las calificaciones están disponibles en el portal académico.',
3
);

INSERT INTO preguntas_frecuentes
(pregunta,respuesta,categoria_id)
VALUES

(
'¿Cómo cambio mi contraseña?',
'Utilice la opción Recuperar contraseña disponible en el portal.',
4
),

(
'¿Cómo cambio mi correo electrónico?',
'Debe ingresar a la sección Perfil y actualizar su correo.',
4
),

(
'¿Qué hago si olvidé mi contraseña?',
'Puede utilizar el proceso de recuperación mediante correo electrónico.',
4
),

(
'¿Cómo reporto un problema técnico?',
'Debe crear un ticket en la sección de soporte.',
4
),

(
'¿Con quién me comunico para recibir ayuda?',
'Puede comunicarse con el departamento de soporte institucional.',
4
);



INSERT INTO palabras_clave (pregunta_id, palabra) VALUES

-- 1
(1,'inscripcion'),
(1,'inscribirme'),
(1,'registro'),
(1,'matricularme'),

-- 2
(2,'fecha limite'),
(2,'inscripcion'),
(2,'fecha'),
(2,'cuando inscribirme'),

-- 3
(3,'modificar datos'),
(3,'actualizar datos'),
(3,'cambiar datos'),
(3,'datos personales'),

-- 4
(4,'documentos'),
(4,'requisitos'),
(4,'inscripcion'),
(4,'papeleria'),

-- 5
(5,'cancelar inscripcion'),
(5,'cancelacion'),
(5,'dar de baja'),
(5,'anular inscripcion'),

-- 6
(6,'metodos de pago'),
(6,'formas de pago'),
(6,'pagar'),
(6,'pagos'),

-- 7
(7,'comprobante'),
(7,'recibo'),
(7,'factura'),
(7,'descargar comprobante'),

-- 8
(8,'pago no registrado'),
(8,'pago pendiente'),
(8,'no aparece pago'),
(8,'validar pago'),

-- 9
(9,'reembolso'),
(9,'devolucion'),
(9,'devolver dinero'),
(9,'solicitar reembolso'),

-- 10
(10,'recargo'),
(10,'mora'),
(10,'pago tardio'),
(10,'penalizacion'),

-- 11
(11,'cursos asignados'),
(11,'mis cursos'),
(11,'cursos'),
(11,'asignacion'),

-- 12
(12,'cambiar curso'),
(12,'cambio de curso'),
(12,'modificar curso'),
(12,'traslado curso'),

-- 13
(13,'programa curso'),
(13,'contenido curso'),
(13,'temario'),
(13,'silabo'),

-- 14
(14,'lista curso'),
(14,'no aparezco'),
(14,'curso asignado'),
(14,'inscripcion curso'),

-- 15
(15,'calificaciones'),
(15,'notas'),
(15,'resultado curso'),
(15,'ver notas'),

-- 16
(16,'cambiar contraseña'),
(16,'password'),
(16,'clave'),
(16,'actualizar contraseña'),

-- 17
(17,'correo'),
(17,'email'),
(17,'cambiar correo'),
(17,'actualizar correo'),

-- 18
(18,'olvide contraseña'),
(18,'recuperar contraseña'),
(18,'reset password'),
(18,'no recuerdo clave'),

-- 19
(19,'problema tecnico'),
(19,'ticket'),
(19,'error sistema'),
(19,'soporte tecnico'),

-- 20
(20,'ayuda'),
(20,'contacto'),
(20,'soporte'),
(20,'asistencia');
