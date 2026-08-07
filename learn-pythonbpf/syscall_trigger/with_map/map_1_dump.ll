source_filename = "map_1_dump.py"
; ModuleID = "map_1_dump.py"
target triple = "bpf"
target datalayout = "e-m:e-p:64:64-i64:64-i128:128-n32:64-S128"

declare i8* @"llvm.bpf.passthrough.p0.p0"(i32 %".1", i8* %".2") nounwind

@"LICENSE" = dso_local global [4 x i8] [i8 71, i8 80, i8 76, i8 0], section "license", align 1
@"user_stats" = dso_local global {ptr, ptr, ptr, ptr} zeroinitializer, section ".maps", align 8, !dbg !22
define dso_local i64 @"tracepoint_syscalls_sys_enter_unlink"(ptr nocapture %".1") noinline nounwind section "tracepoint/syscalls/sys_enter_unlink"
{
entry:
  %"u_id" = alloca i64, align 8
  %"count" = alloca i64*
  %"count_tmp" = alloca i64
  %"__helper_temp_i64_0" = alloca i64, align 8
  %"__helper_temp_i64_0.1" = alloca i64, align 8
  %"__helper_temp_i64_0.2" = alloca i64, align 8
  %"__helper_temp_i64_0.3" = alloca i64, align 8
  %".3" = inttoptr i64 15 to i64 ()*
  %".4" = call i64 %".3"()
  %".5" = and i64 %".4", 4294967295
  store i64 %".5", i64* %"u_id"
  %".7" = load i64, i64* %"u_id"
  %".8" = icmp eq i64 %".7", 1002
  br i1 %".8", label %"if.then", label %"if.end"
if.then:
  %".10" = inttoptr i64 1 to i64* (ptr, ptr)*
  %".11" = call i64* %".10"({ptr, ptr, ptr, ptr}* @"user_stats", i64* %"u_id")
  store i64* %".11", i64** %"count"
  %".13" = load i64*, i64** %"count"
  %".14" = icmp ne i64* %".13", null
  br i1 %".14", label %"if.then.1", label %"if.else"
if.end:
  ret i64 0
if.then.1:
  %".16" = load i64*, i64** %"count"
  %".17" = icmp ne i64* %".16", null
  br i1 %".17", label %"deref_0_not_null", label %"deref_0_merge"
if.end.1:
  br label %"if.end"
if.else:
  store i64 1, i64* %"__helper_temp_i64_0.3"
  %".27" = inttoptr i64 2 to i64 (ptr, ptr, ptr, i64)*
  %".28" = call i64 %".27"({ptr, ptr, ptr, ptr}* @"user_stats", i64* %"u_id", i64* %"__helper_temp_i64_0.3", i64 0)
  br label %"if.end.1"
deref_0_not_null:
  %".19" = load i64, i64* %".16"
  br label %"deref_0_merge"
deref_0_merge:
  %"deref_0_result" = phi  i64 [0, %"if.then.1"], [%".19", %"deref_0_not_null"]
  %".21" = add i64 %"deref_0_result", 1
  store i64 %".21", i64* %"__helper_temp_i64_0.3"
  %".23" = inttoptr i64 2 to i64 (ptr, ptr, ptr, i64)*
  %".24" = call i64 %".23"({ptr, ptr, ptr, ptr}* @"user_stats", i64* %"u_id", i64* %"__helper_temp_i64_0.3", i64 0)
  br label %"if.end.1"
}

@"llvm.compiler.used" = appending global [3 x ptr] [[4 x i8]* @"LICENSE", {ptr, ptr, ptr, ptr}* @"user_stats", i64 (ptr)* @"tracepoint_syscalls_sys_enter_unlink"], section "llvm.metadata"
!llvm.dbg.cu = !{ !1 }
!llvm.module.flags = !{ !24, !25, !26, !27 }
!llvm.ident = !{ !28 }
!0 = !DIFile(directory: "", filename: "map_1_dump.py")
!1 = distinct !DICompileUnit(emissionKind: 1, file: !0, isOptimized: true, language: 29, nameTableKind: 0, producer: "PythonBPF v0.1.9", runtimeVersion: 0, splitDebugInlining: false)
!2 = !DIBasicType(encoding: 7, name: "unsigned int", size: 32)
!3 = !DISubrange(count: 1)
!4 = !{ !3 }
!5 = !DICompositeType(baseType: !2, elements: !4, size: 32, tag: 1)
!6 = !DIDerivedType(baseType: !5, size: 64, tag: 15)
!7 = !DIDerivedType(baseType: !2, size: 64, tag: 15)
!8 = !DIBasicType(encoding: 7, name: "unsigned long long", size: 64)
!9 = !DIDerivedType(baseType: !8, size: 64, tag: 15)
!10 = !DIDerivedType(baseType: !7, file: !0, name: "key", offset: 0, size: 64, tag: 13)
!11 = !DIDerivedType(baseType: !9, file: !0, name: "value", offset: 64, size: 64, tag: 13)
!12 = !DIDerivedType(baseType: !6, file: !0, name: "type", offset: 128, size: 64, tag: 13)
!13 = !DISubrange(count: 1024)
!14 = !{ !13 }
!15 = !DICompositeType(baseType: !2, elements: !14, size: 32768, tag: 1)
!16 = !DIDerivedType(baseType: !15, size: 64, tag: 15)
!17 = !DIDerivedType(baseType: !16, file: !0, name: "max_entries", offset: 192, size: 64, tag: 13)
!18 = !{ !10, !11, !12, !17 }
!19 = distinct !DICompositeType(elements: !18, file: !0, size: 256, tag: 19)
!20 = distinct !DIGlobalVariable(file: !0, isDefinition: true, isLocal: false, name: "user_stats", scope: !1, type: !19)
!21 = !DIExpression()
!22 = !DIGlobalVariableExpression(expr: !21, var: !20)
!23 = !DIBasicType(encoding: 5, name: "long", size: 64)
!24 = !{ i32 1, !"wchar_size", i32 4 }
!25 = !{ i32 7, !"frame-pointer", i32 2 }
!26 = !{ i32 2, !"Debug Info Version", i32 3 }
!27 = !{ i32 7, !"Dwarf Version", i32 5 }
!28 = !{ !"PythonBPF v0.1.9" }
