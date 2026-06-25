import sys

from setuptools import setup
from torch.utils.cpp_extension import BuildExtension, CUDAExtension

extra_link_args = []
if sys.platform == "win32":
    # On PyTorch built with clang-cl, c10.dll does not export the
    # c10::ValueError(SourceLocation, string) constructor inherited via
    # "using Error::Error" -- clang-cl omits dllexport for inherited
    # constructors (llvm/llvm-project#162640).  Headers pulled in by
    # <torch/extension.h> (e.g. ATen/TensorIndexing.h) use TORCH_CHECK_VALUE,
    # which emits a __declspec(dllimport) reference to that constructor, so the
    # link fails with LNK2001.  Alias it to Error(SourceLocation, string), which
    # IS exported; ValueError IS-A Error with no extra data members, so the two
    # constructors are layout- and semantics-identical.
    #
    # Fixed upstream in https://github.com/pytorch/pytorch/pull/175340, which
    # adds the explicit export.  /ALTERNATENAME only supplies a fallback when
    # the symbol is otherwise unresolved, so on a PyTorch that includes that fix
    # the real export resolves and this alias is silently unused -- it is needed
    # only for older builds that predate it.
    _val_imp = (
        "__imp_??0ValueError@c10@@QEAA@USourceLocation@1@"
        "V?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@Z"
    )
    _err_imp = (
        "__imp_??0Error@c10@@QEAA@USourceLocation@1@"
        "V?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@Z"
    )
    extra_link_args.append(f"/ALTERNATENAME:{_val_imp}={_err_imp}")

setup(
    name='quadsim_cuda',
    ext_modules=[
        CUDAExtension('quadsim_cuda', [
            'quadsim.cpp',
            'quadsim_kernel.cu',
            'dynamics_kernel.cu',
        ], extra_link_args=extra_link_args),
    ],
    cmdclass={
        'build_ext': BuildExtension
    })
