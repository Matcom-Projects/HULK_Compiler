#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdbool.h>
#include <stdarg.h>
#include <time.h>

#define OBJECT_DICT_CAPACITY 67

// Imprime un mensaje de error y termina la ejecución del programa
void throw_error(const char *message) {
    fprintf(stderr, "Error: %s\n", message);
    exit(1);
}

// Estructura para almacenar un atributo (clave-valor)
typedef struct attribute {
    char* key;
    void* value;
    struct attribute* next;
} attribute;

// Estructura para un objeto, que contiene una lista de atributos
typedef struct object {
    attribute** lists;
} object;

// Función hash para calcular el índice en la tabla de hash
unsigned int hash(char* key, int capacity) {
    unsigned long hash = 5381;
    int c;
    while ((c = *key++))
        hash = ((hash << 5) + hash) + c;
    return hash % capacity;
}

// Añade un atributo a un objeto
void add_attr(object* obj, char* key, void* value) {
    if (obj == NULL || obj->lists == NULL)
        throw_error("Null Reference");
    unsigned int index = hash(key, OBJECT_DICT_CAPACITY);
    attribute* new_attr = malloc(sizeof(attribute));
    new_attr->key = strdup(key);
    new_attr->value = value;
    new_attr->next = obj->lists[index];
    obj->lists[index] = new_attr;
}

// Obtiene el valor de un atributo de un objeto
void* get_attr_value(object* obj, char* key) {
    if (obj == NULL || obj->lists == NULL)
        throw_error("Null Reference");
    unsigned int index = hash(key, OBJECT_DICT_CAPACITY);
    attribute* current = obj->lists[index];
    while (current != NULL) {
        if (strcmp(current->key, key) == 0) {
            return current->value;
        }
        current = current->next;
    }
    return NULL;
}

// Obtiene el atributo completo de un objeto
attribute* get_attr(object* obj, char* key) {
    if (obj == NULL || obj->lists == NULL)
        throw_error("Null Reference");
    unsigned int index = hash(key, OBJECT_DICT_CAPACITY);
    attribute* current = obj->lists[index];
    while (current != NULL) {
        if (strcmp(current->key, key) == 0) {
            return current;
        }
        current = current->next;
    }
    return NULL;
}

// Reemplaza el valor de un atributo en un objeto
void replace_attr(object* obj, char* key, void* value) {
    if (obj == NULL || obj->lists == NULL)
        throw_error("Null Reference");
    attribute* attr = get_attr(obj, key);
    if (attr != NULL) {
        free(attr->value);
        attr->value = value;
    } else {
        add_attr(obj, key, value);
    }
}

// Elimina un atributo de un objeto
void remove_attr(object* obj, char* key) {
    if (obj == NULL || obj->lists == NULL)
        throw_error("Null Reference");
    unsigned int index = hash(key, OBJECT_DICT_CAPACITY);
    attribute* current = obj->lists[index];
    attribute* previous = NULL;
    while (current != NULL) {
        if (strcmp(current->key, key) == 0) {
            if (previous == NULL) {
                obj->lists[index] = current->next;
            } else {
                previous->next = current->next;
            }
            free(current->key);
            free(current->value);
            free(current);
            return;
        }
        previous = current;
        current = current->next;
    }
}

//Declarations

// Object
object* create_empty_object();
object* create_object();
object* replace_object(object* obj1, object* obj2);
object* method_object_equals(object* obj1, object* obj2);
object* method_object_to_string(object* obj);

// Dynamic
void* get_method(object* obj, char* method_name, char* base_type);
char* get_type(object* obj);
object* is_type(object* obj, char* type);
object* is_protocol(object* obj, char* protocol);

// Print
object* function_print(object* obj);

// Number
object* create_number(double number);
object* copy_object(object* obj);
object* method_number_to_string(object* number);
object* method_number_equals(object* number1, object* number2);
object* perform_numeric_operation(object* num1, object* num2, const char* op);
object* perform_unary_operation(object* num, const char* func);
object* function_parse(object* string);

// String
object* create_string(const char* str);
object* string_concat(object* string1, object* string2);
object* method_string_size(object* self);
object* method_string_to_string(object* str);
object* method_string_equals(object* string1, object* string2);

// Boolean
object* create_boolean(bool boolean);
object* method_boolean_to_string(object* boolean);
object* method_boolean_equals(object* bool1, object* bool2);
object* invert_boolean(object* boolean);
object* boolean_operation(object* bool1, object* bool2, char op);

// Vector
object* create_vector_from_list(int num_elements, object** list);
object* create_vector(int num_elements, ...);
object* method_vector_size(object* self);
object* method_vector_next(object* self);
object* method_vector_current(object* self);
object* get_element_of_vector(object* vector, object* index);
object* method_vector_to_string(object* vector);
object* method_vector_equals(object* vector1, object* vector2);
object* function_range(object* start, object* end);

// Range
object* create_range(object* min, object* max);
object* method_range_next(object* self);
object* method_range_current(object* self);
object* method_range_to_string(object* range);
object* method_range_equals(object* range1, object* range2);

// Definitions
// Crea un objeto vacío
object* create_empty_object() {
    return malloc(sizeof(object));
}

// Copia un objeto
object* copy_object(object* obj) {
    return replace_object(create_empty_object(), obj);
}

// Crea un objeto e inicializa su lista de atributos
object* create_object() {
    object* obj = create_empty_object();
    obj->lists = malloc(sizeof(attribute*) * OBJECT_DICT_CAPACITY);
    for (int i = 0; i < OBJECT_DICT_CAPACITY; i++) {
        obj->lists[i] = NULL;
    }
    add_attr(obj, "method_object_to_string", *method_object_to_string);
    add_attr(obj, "method_object_equals", *method_object_equals);
    return obj;
}

// Reemplaza un objeto con otro
object* replace_object(object* obj1, object* obj2) {
    if (obj1 == NULL && obj2 != NULL)
        obj1 = copy_object(obj2);
    else if (obj1 != NULL && obj2 == NULL)
        obj1->lists = NULL;
    else if (obj1 != NULL && obj2 != NULL)
        obj1->lists = obj2->lists;
    return obj1;
}

// Método para comparar dos objetos
object* method_object_equals(object* obj1, object* obj2) {
    return create_boolean(obj1 == obj2);
}

// Método para convertir un objeto a cadena de texto
object* method_object_to_string(object* obj) {
    char* address = malloc(50);
    sprintf(address, "%p", (void*)obj);
    return create_string(address);
}

// Obtiene el tipo de un objeto
char* get_type(object* obj) {
    if (obj == NULL)
        throw_error("Null Reference");
    return get_attr_value(obj, "parent_type0");
}

// Obtiene un método de un objeto basado en su tipo
void* get_method(object* obj, char* method_name, char* base_type) {
    if (obj == NULL)
        throw_error("Null Reference");
    bool found_base_type = base_type == NULL;
    int index = 0;
    char* initial_parent_type = malloc(128);
    sprintf(initial_parent_type, "%s%d", "parent_type", index++);
    char* type = get_attr_value(obj, initial_parent_type);
    free(initial_parent_type);
    while (type != NULL) {
        if (found_base_type || strcmp(type, base_type) == 0) {
            found_base_type = true;
            char* full_name = malloc(128);
            sprintf(full_name, "%s%s%s%s", "method_", type, "_", method_name);
            void* method = get_attr_value(obj, full_name);
            free(full_name);
            if (method != NULL)
                return method;
        }
        char* parent_type = malloc(128);
        sprintf(parent_type, "%s%d", "parent_type", index++);
        type = get_attr_value(obj, parent_type);
        free(parent_type);
    }
    return NULL;
}

// Verifica si un objeto es de un tipo específico
object* is_type(object* obj, char* type) {
    if (obj == NULL)
        throw_error("Null Reference");
    int index = 0;
    char* initial_parent_type = malloc(128);
    sprintf(initial_parent_type, "%s%d", "parent_type", index++);
    char* ptype = get_attr_value(obj, initial_parent_type);
    free(initial_parent_type);
    while (ptype != NULL) {
        if (strcmp(ptype, type) == 0)
            return create_boolean(true);
        char* parent_type = malloc(128);
        sprintf(parent_type, "%s%d", "parent_type", index++);
        ptype = get_attr_value(obj, parent_type);
        free(parent_type);
    }
    return create_boolean(false);
}

// Verifica si un objeto cumple con un protocolo específico
object* is_protocol(object* obj, char* protocol) {
    if (obj == NULL)
        throw_error("Null Reference");
    int index = 0;
    char* initial_protocol = malloc(128);
    sprintf(initial_protocol, "%s%d", "conforms_protocol", index++);
    char* pprotocol = get_attr_value(obj, initial_protocol);
    free(initial_protocol);
    while (pprotocol != NULL) {
        if (strcmp(pprotocol, protocol) == 0)
            return create_boolean(true);
        char* cprotocol = malloc(128);
        sprintf(cprotocol, "%s%d", "conforms_protocol", index++);
        pprotocol = get_attr_value(obj, cprotocol);
        free(cprotocol);
    }
    return create_boolean(false);
}

// Función para imprimir un objeto
object* function_print(object* obj) {
    if (obj == NULL || obj->lists == NULL) {
        printf("Null\n");
        return create_string("Null");
    }
    object* str = ((object* (*)(object*))get_method(obj, "to_string", 0))(obj);
    char* value = get_attr_value(str, "value");
    printf("%s\n", value);
    return str;
}

// Crea un objeto de tipo número
object* create_number(double number) {
    object* obj = create_object();
    double* value = malloc(sizeof(double));
    *value = number;
    add_attr(obj, "value", value);
    add_attr(obj, "parent_type0", "number");
    add_attr(obj, "parent_type1", "object");
    add_attr(obj, "method_number_to_string", *method_number_to_string);
    add_attr(obj, "method_number_equals", *method_number_equals);
    return obj;
}
// Método para convertir un número a cadena de texto
object* method_number_to_string(object* number) {
    if (number == NULL)
        throw_error("Null Reference");
    double* value = get_attr_value(number, "value");
    char* str = malloc(30);
    sprintf(str, "%f", *value);
    return create_string(str);
}

// Función para parsear un string a un número
object* function_parse(object* string) {
    if (string == NULL)
        throw_error("Null Reference");
    char* value = get_attr_value(string, "value");
    return create_number(strtod(value, NULL));
}

// Realiza una operación numérica entre dos números
object* perform_numeric_operation(object* num1, object* num2, const char *op) {
    if (num1 == NULL || num2 == NULL)
        throw_error("Null Reference");

    double* value1 = get_attr_value(num1, "value");
    double* value2 = get_attr_value(num2, "value");

    double result;

    if (strcmp(op, "plus") == 0) {
        result = *value1 + *value2;
    } else if (strcmp(op, "minus") == 0) {
        result = *value1 - *value2;
    } else if (strcmp(op, "star") == 0) {
        result = *value1 * *value2;
    } else if (strcmp(op, "div") == 0) {
        if (*value2 == 0)
            throw_error("Division by Zero");
        result = *value1 / *value2;
    } else if (strcmp(op, "pow") == 0) {
        result = pow(*value1, *value2);
    } else if (strcmp(op, "mod") == 0) {
        result = (int)*value1 % (int)*value2;
    } else {
        throw_error("Unknown Operation");
    }

    return create_number(result);
}

// Realiza una comparación booleana entre dos números
object* perform_boolean_comparison(object* obj1, object* obj2, const char *comp) {
    if (obj1 == NULL || obj2 == NULL)
        throw_error("Null Reference");

    double* value1 = get_attr_value(obj1, "value");
    double* value2 = get_attr_value(obj2, "value");

    bool result;

    if (strcmp(comp, "equal") == 0) {
        result = fabs(*value1 - *value2) < 0.000000001;
    } else if (strcmp(comp, "less_than") == 0) {
        result = *value1 < *value2;
    } else if (strcmp(comp, "less_or_eq") == 0) {
        result = *value1 <= *value2;
    } else if (strcmp(comp, "greater_than") == 0) {
        result = *value1 > *value2;
    } else if (strcmp(comp, "greater_or_eq") == 0) {
        result = *value1 >= *value2;
    } else {
        throw_error("Unknown Comparison");
    }

    return create_boolean(result);
}

// Realiza una operación unaria numérica
object* perform_unary_operation(object* num, const char *func) {
    if (num == NULL && strcmp(func, "rand") != 0)
        throw_error("Null Reference");

    double* value = get_attr_value(num, "value");

    if (strcmp(func, "sqrt") == 0) {
        return create_number(sqrt(*value));
    } else if (strcmp(func, "sin") == 0) {
        return create_number(sin(*value));
    } else if (strcmp(func, "cos") == 0) {
        return create_number(cos(*value));
    } else if (strcmp(func, "exp") == 0) {
        return create_number(exp(*value));
    } else if (strcmp(func, "log") == 0) {
        return create_number(log(*value));
    } else if (strcmp(func, "rand") == 0) {
        return create_number((double)rand() / (RAND_MAX + 1.0));
    } else {
        throw_error("Unknown Operation");
    }

    return NULL;
}

// Crea un objeto de tipo string
object* create_string(const char* str) {
    object* obj = create_object();
    add_attr(obj, "value", strdup(str));
    add_attr(obj, "parent_type0", "string");
    add_attr(obj, "parent_type1", "object");
    int* len = malloc(sizeof(int));
    *len = strlen(str);
    add_attr(obj, "len", len);
    return obj;
}

// Método para concatenar dos strings
object* string_concat(object* obj1, object* obj2, bool space) {
    if (obj1 == NULL || obj2 == NULL)
        throw_error("Null Reference");
    char* str1 = get_attr_value(obj1, "value");
    char* str2 = get_attr_value(obj2, "value");
    int len1 = strlen(str1);
    int len2 = strlen(str2);
    char* result;
    if (space) {
        result = malloc((len1 + len2 + 2) * sizeof(char));
        strcpy(result, str1);
        result[len1] = ' ';
        strcpy(result + len1 + 1, str2);
    } else {
        result = malloc((len1 + len2 + 1) * sizeof(char));
        strcpy(result, str1);
        strcat(result, str2);
    }
    return create_string(result);
}

// Método para obtener el tamaño de un string
object* method_string_size(object* self) {
    if (self == NULL)
        throw_error("Null Reference");
    return create_number(*(int*)get_attr_value(self, "len"));
}

// Método para convertir un string a cadena de texto (es redundante pero necesario para el sistema de métodos)
object* method_string_to_string(object* str) {
    if (str == NULL)
        throw_error("Null Reference");
    return str;
}

// Método para comparar dos strings
object* method_string_equals(object* string1, object* string2) {
    if (string1 == NULL || string2 == NULL)
        throw_error("Null Reference");
    char* value1 = get_attr_value(string1, "value");
    char* value2 = get_attr_value(string2, "value");
    return create_boolean(strcmp(value1, value2) == 0);
}

// Crea un objeto de tipo booleano
object* create_boolean(bool boolean) {
    object* obj = create_object();
    bool* value = malloc(sizeof(bool));
    *value = boolean;
    add_attr(obj, "value", value);
    add_attr(obj, "parent_type0", "boolean");
    add_attr(obj, "parent_type1", "object");
    return obj;
}

// Método para convertir un booleano a cadena de texto
object* method_boolean_to_string(object* boolean) {
    if (boolean == NULL)
        throw_error("Null Reference");
    bool* value = get_attr_value(boolean, "value");
    if (*value)
        return create_string("true");
    else
        return create_string("false");
}

// Método para comparar dos booleanos
object* method_boolean_equals(object* bool1, object* bool2) {
    if (bool1 == NULL || bool2 == NULL)
        throw_error("Null Reference");
    bool* value1 = get_attr_value(bool1, "value");
    bool* value2 = get_attr_value(bool2, "value");
    return create_boolean(*value1 == *value2);
}

// Invierte el valor de un booleano
object* invert_boolean(object* boolean) {
    if (boolean == NULL)
        throw_error("Null Reference");
    bool* value = get_attr_value(boolean, "value");
    return create_boolean(!*value);
}

// Realiza una operación lógica entre dos booleanos
object* boolean_operation(object* bool1, object* bool2, char op) {
    if (bool1 == NULL || bool2 == NULL)
        throw_error("Null Reference");
    bool vbool1 = *(bool*)get_attr_value(bool1, "value");
    bool vbool2 = *(bool*)get_attr_value(bool2, "value");
    if (op == '|')
        return create_boolean(vbool1 || vbool2);
    if (op == '&')
        return create_boolean(vbool1 && vbool2);
    return create_boolean(false);
}

// Crea un objeto de tipo vector a partir de una lista
object* create_vector_from_list(int num_elements, object** list) {
    object* vector = create_object();
    add_attr(vector, "parent_type0", "vector");
    add_attr(vector, "parent_type1", "object");
    int* size = malloc(sizeof(int));
    *size = num_elements;
    add_attr(vector, "size", size);
    add_attr(vector, "list", list);
    add_attr(vector, "current", create_number(-1));
    return vector;
}

// Crea un objeto de tipo vector con un número variable de elementos
object* create_vector(int num_elements, ...) {
    va_list elements;
    va_start(elements, num_elements);
    object** list = malloc(num_elements * sizeof(object*));
    for (int i = 0; i < num_elements; i++) {
        list[i] = va_arg(elements, object*);
    }
    va_end(elements);
    return create_vector_from_list(num_elements, list);
}

// Método para obtener el tamaño de un vector
object* method_vector_size(object* self) {
    if (self == NULL)
        throw_error("Null Reference");
    return create_number(*(int*)get_attr_value(self, "size"));
}

// Método para obtener el siguiente elemento de un vector
object* method_vector_next(object* self) {
    if (self == NULL)
        throw_error("Null Reference");
    int size = *(int*)get_attr_value(self, "size");
    double* current = get_attr_value((object*)get_attr_value(self, "current"), "value");
    if (*current + 1 < size) {
        *current += 1;
        return create_boolean(true);
    }
    return create_boolean(false);
}

// Método para obtener el elemento actual de un vector
object* method_vector_current(object* self) {
    if (self == NULL)
        throw_error("Null Reference");
    return get_element_of_vector(self, get_attr_value(self, "current"));
}

// Función para obtener un elemento de un vector dado un índice
object* get_element_of_vector(object* vector, object* index) {
    if (vector == NULL || index == NULL)
        throw_error("Null Reference");
    int i = (int)*(double*)get_attr_value(index, "value");
    int size = *(int*)get_attr_value(vector, "size");
    if (i >= size)
        throw_error("Index out of range");
    return ((object**)get_attr_value(vector, "list"))[i];
}

// Método para convertir un vector a cadena de texto
object* method_vector_to_string(object* vector) {
    if (vector == NULL)
        throw_error("Null Reference");
    int* size = get_attr_value(vector, "size");
    int total_size = 3 + ((*size > 0 ? *size : 1) - 1) * 2;
    object** list = get_attr_value(vector, "list");
    object** strs = malloc(*size * sizeof(object*));
    for (int i = 0; i < *size; i++) {
        strs[i] = ((object* (*)(object*))get_method(list[i], "to_string", 0))(list[i]);
        total_size += *(int*)get_attr_value(strs[i], "len");
    }
    char* result = malloc(total_size * sizeof(char));
    result[0] = '\0';
    strcat(result, "[");
    for (int i = 0; i < *size; i++) {
        strcat(result, (char*)get_attr_value(strs[i], "value"));
        free(strs[i]);
        if (i + 1 < *size)
            strcat(result, ", ");
    }
    strcat(result, "]");
    free(strs);
    return create_string(result);
}

// Método para comparar dos vectores
object* method_vector_equals(object* vector1, object* vector2) {
    if (vector1 == NULL || vector2 == NULL)
        throw_error("Null Reference");
    if (strcmp(get_type(vector1), "vector") != 0 || strcmp(get_type(vector2), "vector") != 0)
        return create_boolean(false);
    int* size1 = get_attr_value(vector1, "size");
    object** list1 = get_attr_value(vector1, "list");
    int* size2 = get_attr_value(vector2, "size");
    object** list2 = get_attr_value(vector2, "list");
    if (*size1 != *size2)
        return create_boolean(false);
    for (int i = 0; i < *size1; i++) {
        bool* equal = get_attr_value(((object* (*)(object*, object*))get_method(list1[i], "equals", 0))(list1[i], list2[i]), "value");
        if (!*equal)
            return create_boolean(false);
    }
    return create_boolean(true);
}

// Función para crear un rango entre dos objetos
object* function_range(object* start, object* end) {
    if (start == NULL || end == NULL)
        throw_error("Null Reference");
    return create_range(start, end);
}

// Crea un objeto de tipo rango
object* create_range(object* min, object* max) {
    if (min == NULL || max == NULL)
        throw_error("Null Reference");
    object* obj = create_object();
    add_attr(obj, "min", min);
    add_attr(obj, "max", max);
    add_attr(obj, "current", number_minus(min, create_number(1)));
    int* size = malloc(sizeof(int));
    *size = (int)(*(double*)get_attr_value(max, "value")) - (int)(*(double*)get_attr_value(min, "value"));
    add_attr(obj, "size", size);
    add_attr(obj, "parent_type0", "range");
    add_attr(obj, "parent_type1", "object");
    add_attr(obj, "conforms_protocol0", "iterable");
    add_attr(obj, "method_range_next", *method_range_next);
    add_attr(obj, "method_range_current", *method_range_current);
    add_attr(obj, "method_range_to_string", *method_range_to_string);
    add_attr(obj, "method_range_equals", *method_range_equals);
    return obj;
}

// Método para obtener el siguiente elemento de un rango
object* method_range_next(object* self) {
    if (self == NULL)
        throw_error("Null Reference");
    int max = *(double*)get_attr_value((object*)get_attr_value(self, "max"), "value");
    double* current = get_attr_value((object*)get_attr_value(self, "current"), "value");
    if (*current + 1 < max) {
        *current += 1;
        return create_boolean(true);
    }
    return create_boolean(false);
}

// Método para obtener el elemento actual de un rango
object* method_range_current(object* self) {
    if (self == NULL)
        throw_error("Null Reference");
    return get_attr_value(self, "current");
}

// Método para convertir un rango a cadena de texto
object* method_range_to_string(object* range) {
    if (range == NULL)
        throw_error("Null Reference");
    object* min = get_attr_value(range, "min");
    object* max = get_attr_value(range, "max");
    int total_size = 6;
    object* min_str = ((object* (*)(object*))get_method(min, "to_string", 0))(min);
    total_size += *(int*)get_attr_value(min_str, "len");
    object* max_str = ((object* (*)(object*))get_method(max, "to_string", 0))(max);
    total_size += *(int*)get_attr_value(max_str, "len");
    char* result = malloc(total_size * sizeof(char));
    sprintf(result, "[%s - %s]", (char*)get_attr_value(min_str, "value"), (char*)get_attr_value(max_str, "value"));
    free(min_str);
    free(max_str);
    return create_string(result);
}

// Método para comparar dos rangos
object* method_range_equals(object* range1, object* range2) {
    if (range1 == NULL || range2 == NULL)
        throw_error("Null Reference");
    if (strcmp(get_type(range1), "range") != 0 || strcmp(get_type(range2), "range") != 0)
        return create_boolean(false);
    object* min1 = get_attr_value(range1, "min");
    object* max1 = get_attr_value(range1, "max");
    object* min2 = get_attr_value(range2, "min");
    object* max2 = get_attr_value(range2, "max");
    return boolean_operation(method_number_equals(min1, min2), method_number_equals(max1, max2), '&');
}