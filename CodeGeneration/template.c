#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdbool.h>
#include <stdarg.h>
#include <time.h>

#define OBJECT_DICT_CAPACITY 67

void throw_error(const char *message) {
    fprintf(stderr, "Error: %s\n", message);
    exit(1);
}

typedef struct attribute {
    char* key;
    void* value;
    struct attribute* next;
} attribute;

typedef struct object {
    attribute** lists;
} object;

unsigned int hash(char* key, int capacity) {
    unsigned long hash = 5381;
    int c;
    while ((c = *key++))
        hash = ((hash << 5) + hash) + c;
    return hash % capacity;
}

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

void replace_attr(object* obj, char* key, void* value) {
    if (obj == NULL || obj->lists == NULL)
        throw_error("Null Reference");
    attribute* attr = get_attr(obj, key);
    free(attr->value);
    attr->value = value;
}

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

object* create_empty_object() {
    return malloc(sizeof(object));
}

object* copy_object(object* obj) {
    return replace_object(create_empty_object(), obj);
}

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

object* replace_object(object* obj1, object* obj2) {
    if (obj1 == NULL && obj2 != NULL)
        obj1 = copy_object(obj2);
    else if (obj1 != NULL && obj2 == NULL)
        obj1->lists = NULL;
    else if (obj1 != NULL && obj2 != NULL)
        obj1->lists = obj2->lists;
    return obj1;
}

object* method_object_equals(object* obj1, object* obj2) {
    return create_boolean(obj1 == obj2);
}

object* method_object_to_string(object* obj) {
    char* address = malloc(50);
    sprintf(address, "%p", (void*)obj);
    return create_string(address);
}

char* get_type(object* obj) {
    if (obj == NULL)
        throw_error("Null Reference");
    return get_attr_value(obj, "parent_type0");
}

void* get_method_for_current_type(object* obj, char* method_name, char* base_type) {
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

object* function_print(object* obj) {
    if (obj == NULL || obj->lists == NULL) {
        printf("Null\n");
        return create_string("Null");
    }
    object* str = ((object* (*)(object*))get_method_for_current_type(obj, "to_string", 0))(obj);
    char* value = get_attr_value(str, "value");
    printf("%s\n", value);
    return str;
}

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

object* method_number_to_string(object* number) {
    if (number == NULL)
        throw_error("Null Reference");
    double* value = get_attr_value(number, "value");
    char* str = malloc(30);
    sprintf(str, "%f", *value);
    return create_string(str);
}

object* function_parse(object* string) {
    if (string == NULL)
        throw_error("Null Reference");
    char* value = get_attr_value(string, "value");
    return create_number(strtod(value, NULL));
}

typedef enum {
    plus,
    minus,
    star,
    div,
    pow,
    mod
} OperationType;

object* perform_numeric_operation(object* num1, object* num2, OperationType op) {
    if (num1 == NULL || num2 == NULL)
        throw_error("Null Reference");

    double* value1 = get_attr_value(num1, "value");
    double* value2 = get_attr_value(num2, "value");

    double result;
    switch (op) {
        case plus:
            return create_number(*value1 + *value2);
        case minus:
            return create_number(*value1 - *value2);
        case star:
            return create_number(*value1 * *value2);
        case div:
            if (*value2 == 0)
                throw_error("Division by Zero");
            return create_number(*value1 / *value2);
        case pow:
            return create_number(pow(*value1, *value2));
        case mod:
            return create_number(((int)*value1) % ((int)*value2));
        default:
            throw_error("Unknown Operation");
    }

    return create_number(result);
}

typedef enum {
    equal,
    less_than,
    less_or_eq,
    greater_than,
    greater_or_eq
} ComparisonType;

object* perform_boolean_comparison(object* obj1, object* obj2, ComparisonType comp) {
    if (obj1 == NULL || obj2 == NULL)
        throw_error("Null Reference");

    double* value1 = get_attr_value(obj1, "value");
    double* value2 = get_attr_value(obj2, "value");

    bool result;
    switch (comp) {
        case equal:
            if (strcmp(get_type(number1), "number") != 0 || strcmp(get_type(number2), "number") != 0)
                return create_number(false);
            else {
              return create_number(fabs(*value1 - *value2) < 0.000000001);
            }
            break;
        case less_than:
            return create_number(*value1 < *value2);
        case less_or_eq:
            return create_number(*value1 <= *value2);
        case greater_than:
            return create_number(*value1 > *value2);
        case greater_or_eq:
            return create_number(*value1 >= *value2);
        default:
            throw_error("Unknown Comparison");
    }

    return 0;
}

typedef enum {
    sqrt,
    sin,
    cos,
    exp,
    log,
    rand
} FunctionType;

object* perform_numeric_operation(object* num, FunctionType func) {
    if (num1 == NULL && func != rand)
        throw_error("Null Reference");
    else if (func == rand) {
      return create_number((double)rand() / (RAND_MAX + 1.0));
    }

    double* value = get_attr_value(num, "value");

    switch (func) {
        case sqrt:
            return create_number(sqrt(value));
        case sin:
            return create_number(sin(value));
        case cos:
            return create_number(cos(value));
        case exp:
            return create_number(exp(value));
        case log:
            return create_number(log(value));
        default:
            throw_error("Unknown Operation");
    }

    return 0;
}

object* create_string(char* str) {
    object* obj = create_object();
    add_attr(obj, "value", str);
    add_attr(obj, "parent_type0", "string");
    add_attr(obj, "parent_type1", "object");
    int* len = malloc(sizeof(int));
    *len = strlen(str);
    add_attr(obj, "len", len);
    add_attr(obj, "method_string_to_string", *method_string_to_string);
    add_attr(obj, "method_string_equals", *method_string_equals);
    add_attr(obj, "method_string_size", *method_string_size);
    return obj;
}

object* string_concat(object* obj1, object* obj2) {
    if (obj1 == NULL || obj2 == NULL)
        throw_error("Null Reference");
    object* string1 = ((object* (*)(object*))get_method_for_current_type(obj1, "to_string", NULL))(obj1);
    object* string2 = ((object* (*)(object*))get_method_for_current_type(obj2, "to_string", NULL))(obj2);
    char* str1 = get_attr_value(string1, "value");
    int len1 = *(int*)get_attr_value(string1, "len");
    char* str2 = get_attr_value(string2, "value");
    int len2 = *(int*)get_attr_value(string2, "len");
    char* result = malloc((len1 + len2 + 1) * sizeof(char));
    sprintf(result, "%s%s", str1, str2);
    result[len1 + len2] = '\0';
    return create_string(result);
}

object* method_string_size(object* self) {
    if (self == NULL)
        throw_error("Null Reference");
    return create_number(*(int*)get_attr_value(self, "len"));
}

object* method_string_to_string(object* str) {
    if (str == NULL)
        throw_error("Null Reference");
    return str;
}

object* method_string_equals(object* string1, object* string2) {
    if (string1 == NULL || string2 == NULL)
        throw_error("Null Reference");
    if (strcmp(get_type(string1), "string") != 0 || strcmp(get_type(string2), "string") != 0)
        return create_boolean(false);
    char* value1 = get_attr_value(string1, "value");
    char* value2 = get_attr_value(string2, "value");
    return create_boolean(strcmp(value1, value2) == 0);
}

object* create_boolean(bool boolean) {
    object* obj = create_object();
    bool* value = malloc(sizeof(bool));
    *value = boolean;
    add_attr(obj, "value", value);
    add_attr(obj, "parent_type0", "boolean");
    add_attr(obj, "parent_type1", "object");
    add_attr(obj, "method_boolean_to_string", *method_boolean_to_string);
    add_attr(obj, "method_boolean_equals", *method_boolean_equals);
    return obj;
}

object* method_boolean_to_string(object* boolean) {
    if (boolean == NULL)
        throw_error("Null Reference");
    bool* value = get_attr_value(boolean, "value");
    if (*value == true)
        return create_string("true");
    else
        return create_string("false");
}

object* method_boolean_equals(object* bool1, object* bool2) {
    if (bool1 == NULL || bool2 == NULL)
        throw_error("Null Reference");
    if (strcmp(get_type(bool1), "boolean") != 0 || strcmp(get_type(bool2), "boolean") != 0)
        return create_boolean(false);
    bool* value1 = get_attr_value(bool1, "value");
    bool* value2 = get_attr_value(bool2, "value");
    return create_boolean(value1 == value2);
}

object* invert_boolean(object* boolean) {
    if (boolean == NULL)
        throw_error("Null Reference");
    bool* value = get_attr_value(boolean, "value");
    return create_boolean(!*value);
}

object* boolean_operation(object* bool1, object* bool2, char op) {
    if (bool1 == NULL || bool2 == NULL)
        throw_error("Null Reference");
    bool vbool1 = *(bool*)get_attr_value(bool1, "value");
    bool vbool2 = *(bool*)get_attr_value(bool2, "value");
    if (op == '|') return create_boolean(vbool1 || vbool2);
    if (op == '&') return create_boolean(vbool1 && vbool2);
    return create_boolean(false); // Default case, shouldn't reach here
}

object* create_vector_from_list(int num_elements, object** list) {
    object* vector = create_object();
    add_attr(vector, "parent_type0", "vector");
    add_attr(vector, "parent_type1", "object");
    add_attr(vector, "conforms_protocol0", "iterable");
    add_attr(vector, "method_vector_to_string", *method_vector_to_string);
    add_attr(vector, "method_vector_equals", *method_vector_equals);
    int* size = malloc(sizeof(int));
    *size = num_elements;
    add_attr(vector, "size", size);
    add_attr(vector, "list", list);
    add_attr(vector, "current", create_number(-1));
    add_attr(vector, "method_vector_size", *method_vector_size);
    add_attr(vector, "method_vector_next", *method_vector_next);
    add_attr(vector, "method_vector_current", *method_vector_current);
    return vector;
}

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

object* method_vector_size(object* self) {
    if (self == NULL)
        throw_error("Null Reference");
    return create_number(*(int*)get_attr_value(self, "size"));
}

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

object* method_vector_current(object* self) {
    if (self == NULL)
        throw_error("Null Reference");
    return get_element_of_vector(self, get_attr_value(self, "current"));
}

object* get_element_of_vector(object* vector, object* index) {
    if (vector == NULL || index == NULL)
        throw_error("Null Reference");
    int i = (int)*(double*)get_attr_value(index, "value");
    int size = *(int*)get_attr_value(vector, "size");
    if (i >= size)
        throw_error("Index out of range");
    return ((object**)get_attr_value(vector, "list"))[i];
}

object* method_vector_to_string(object* vector) {
    if (vector == NULL)
        throw_error("Null Reference");
    int* size = get_attr_value(vector, "size");
    int total_size = 3 + ((*size > 0 ? *size : 1) - 1) * 2;
    object** list = get_attr_value(vector, "list");
    object** strs = malloc(*size * sizeof(object*));
    for (int i = 0; i < *size; i++) {
        strs[i] = ((object* (*)(object*))get_method_for_current_type(list[i], "to_string", 0))(list[i]);
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
        bool* equal = get_attr_value(((object* (*)(object*, object*))get_method_for_current_type(list1[i], "equals", 0))(list1[i], list2[i]), "value");
        if (!*equal)
            return create_boolean(false);
    }
    return create_boolean(true);
}

object* function_range(object* start, object* end) {
    if (start == NULL || end == NULL)
        throw_error("Null Reference");
    return create_range(start, end);
}

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

object* method_range_current(object* self) {
    if (self == NULL)
        throw_error("Null Reference");
    return get_attr_value(self, "current");
}

object* method_range_to_string(object* range) {
    if (range == NULL)
        throw_error("Null Reference");
    object* min = get_attr_value(range, "min");
    object* max = get_attr_value(range, "max");
    int total_size = 6;
    object* min_str = ((object* (*)(object*))get_method_for_current_type(min, "to_string", 0))(min);
    total_size += *(int*)get_attr_value(min_str, "len");
    object* max_str = ((object* (*)(object*))get_method_for_current_type(max, "to_string", 0))(max);
    total_size += *(int*)get_attr_value(max_str, "len");
    char* result = malloc(total_size * sizeof(char));
    sprintf(result, "[%s - %s]", (char*)get_attr_value(min_str, "value"), (char*)get_attr_value(max_str, "value"));
    free(min_str);
    free(max_str);
    return create_string(result);
}

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
