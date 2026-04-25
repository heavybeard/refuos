# Local Dictionaries

This folder is for **private, stack-specific dictionaries** that extend the public `refuos-dev` package without exposing your tech stack to the world.

Files in this folder named `*.txt` are **gitignored** — they are never committed. This README is the only file tracked here.

## How it works

Any `.txt` file you drop here is automatically picked up by `generate_espanso.py` and generates a private Espanso package named `refuos-local-<name>.yml`.

For example, if you create `local/frontend.txt`, running the generator produces `refuos-local-frontend.yml` in your Espanso match directory.

Local packs are:

- Included in the default `python3 generate_espanso.py` run
- Included in `--output-dir` output
- **Excluded** from `--espanso-packages` (they are private, not for the Hub)

## Creating a local dictionary

1. Create a `.txt` file in this folder. Name it after your stack or context (e.g. `react.txt`, `django.txt`, `mycompany.txt`).
2. Add one word per line. Lines starting with `#` are comments.
3. Run `python3 generate_espanso.py` (or `--check` to validate only).
4. Restart Espanso: `espanso restart`.

```text
# local/react.txt — React-specific hooks and patterns
useState
useEffect
useCallback
useMemo
useRef
useContext
className
children
onClick
onChange
```

## Validation rules

The generator validates local dictionaries with the same rules as public ones:

The generator validates local dictionaries with the same rules as public ones:

- No duplicate words within a file
- No word that already exists in a public dictionary (`italiano.txt`, `accenti.txt`, `dev.txt`)
- No word that already exists in another local file

Validation errors block generation. Fix them before running.

## Example starters

Below are ready-to-copy starters for common stacks.

### React (`local/react.txt`)

```text
# React hooks
useState
useEffect
useCallback
useMemo
useRef
useContext
useReducer
useLayoutEffect
useTransition
useDeferredValue
useId
# API
forwardRef
createContext
createPortal
# Patterns
className
children
onClick
onChange
onSubmit
props
```

### Vue (`local/vue.txt`)

```text
# Composition API
defineComponent
defineProps
defineEmits
defineExpose
defineSlots
# Reactivity
reactive
computed
watchEffect
toRef
toRefs
shallowRef
# Lifecycle
onMounted
onUpdated
onUnmounted
```

### Angular (`local/angular.txt`)

```text
# Decorators
NgModule
ViewChild
ContentChild
HostListener
HostBinding
# RxJS
BehaviorSubject
ReplaySubject
switchMap
mergeMap
concatMap
exhaustMap
takeUntil
debounceTime
distinctUntilChanged
combineLatest
```

### Django (`local/django.txt`)

```text
# ORM fields
CharField
IntegerField
ForeignKey
ManyToManyField
TextField
BooleanField
DateTimeField
# Concepts
queryset
viewset
urlpatterns
makemigrations
collectstatic
```

### NestJS / Fastify (`local/nestjs.txt`)

```text
nestjs
fastify
mercurius
prisma
kysely
ioredis
throttler
```

### Data Science (`local/datascience.txt`)

```text
dataframe
tensor
epoch
gradient
hyperparameter
overfitting
preprocessing
tokenizer
embedding
inference
backpropagation
pandas
numpy
matplotlib
scikit
tensorflow
pytorch
```
