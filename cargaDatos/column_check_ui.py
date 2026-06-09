"""UI para la pantalla de resultados del chequeo preventivo de columnas."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import streamlit as st

_CATEGORY_LABELS = {
    "missing": "Columnas faltantes",
    "auto_resolved": "Completadas automáticamente",
    "not_applicable": "No usadas en este reporte",
}

_CATEGORY_ICONS = {
    "missing": "⚠️",
    "auto_resolved": "ℹ️",
    "not_applicable": "➖",
}


def _format_used_columns(used_columns: List[Dict[str, Any]]) -> str:
    labels = [str(c.get("label") or c.get("column_name") or c.get("canonical")) for c in used_columns]
    labels = [label for label in labels if label and label != "None"]
    return ", ".join(labels)


def render_column_check_review(result: Dict[str, Any], *, embedded: bool = True) -> None:
    """Muestra resultados del endpoint check_columns y botones Continuar / Cancelar."""
    if embedded:
        st.subheader("Chequeo de columnas")
    else:
        st.title("Chequeo de columnas")
    input_label = result.get("input_key")
    input_keys = result.get("input_keys")
    if input_keys:
        archivos_txt = ", ".join(f"`{n}`" for n in input_keys)
    elif input_label:
        archivos_txt = f"`{input_label}`"
    else:
        archivos_txt = "—"

    st.caption(
        f"Reporte: `{result.get('report_id', '—')}` · "
        f"Perfil: {result.get('profile_name') or result.get('profile', '—')} · "
        f"Archivos: {archivos_txt}"
    )

    status = result.get("status", "")
    rows = result.get("rows")
    if rows is not None:
        st.metric("Filas analizadas", rows)

    if status in ("ok", "complete"):
        st.success("No se detectaron advertencias en las columnas esperadas.")
    elif status == "has_warnings":
        st.warning("Se detectaron advertencias. Puede continuar si el timestamp es válido.")
    elif status == "timestamp_error":
        st.error("No se puede generar el reporte: problema con la columna de fecha/hora.")
    elif status in ("error", "failed"):
        st.error(result.get("message") or result.get("error") or "Error al revisar las columnas.")

    timestamp = result.get("timestamp") or {}
    if status not in ("error", "failed"):
        if timestamp.get("ok"):
            st.success(timestamp.get("message") or "Timestamp válido.")
        else:
            st.error(timestamp.get("message") or "Timestamp no válido.")

    counts = result.get("counts") or {}
    if counts:
        c0, c1, c2, c3 = st.columns(4)
        c0.metric("Disponibles", counts.get("present", 0))
        c1.metric("Faltantes", counts.get("missing", 0))
        c2.metric("Auto-resueltas", counts.get("auto_resolved", 0))
        c3.metric("No usadas", counts.get("not_applicable", 0))

    columns = result.get("columns") or {}
    present_columns: List[Dict[str, Any]] = columns.get("present") or []
    if present_columns:
        with st.expander(f"✅ Columnas disponibles ({len(present_columns)})", expanded=False):
            max_items = 60
            for col in present_columns[:max_items]:
                label = col.get("expected_column_name") or col.get("mapped_column_name") or col.get("canonical")
                canonical = col.get("canonical")
                if canonical and canonical != label:
                    st.markdown(f"- **{label}** → `{canonical}`")
                else:
                    st.markdown(f"- **{label}**")
            if len(present_columns) > max_items:
                st.caption(f"Mostrando {max_items} de {len(present_columns)} columnas disponibles.")

    warnings: List[Dict[str, Any]] = result.get("warnings") or []
    if warnings:
        st.subheader("Detalle de advertencias")
        by_category: Dict[str, List[Dict[str, Any]]] = {}
        for w in warnings:
            cat = w.get("category") or "other"
            by_category.setdefault(cat, []).append(w)

        for cat, items in by_category.items():
            label = _CATEGORY_LABELS.get(cat, cat)
            icon = _CATEGORY_ICONS.get(cat, "•")
            with st.expander(f"{icon} {label} ({len(items)})", expanded=(cat == "missing")):
                for w in items:
                    title = w.get("expected_column_name") or w.get("canonical") or "Aviso"
                    st.markdown(f"**{title}**")
                    if w.get("message"):
                        st.write(w["message"])
                    used_text = _format_used_columns(w.get("used_columns") or [])
                    if used_text:
                        st.caption(f"Se usó: {used_text}")
                    if w.get("formula"):
                        st.caption(f"Fórmula: {w['formula']}")
                    if w.get("detail"):
                        st.caption(w["detail"])

    saved = result.get("saved_to")
    if isinstance(saved, dict) and saved.get("s3_uri"):
        st.caption(f"Resultado guardado en: {saved['s3_uri']}")

    can_continue = bool(result.get("can_generate_report"))
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if can_continue:
            if st.button(
                "Continuar con la generación",
                type="primary",
                use_container_width=True,
                key="btn_column_check_continue",
            ):
                st.session_state.carga_fase = "upload_rest"
                st.rerun()
        else:
            st.button(
                "Continuar con la generación",
                disabled=True,
                use_container_width=True,
                help="Corrija el archivo (timestamp) o suba otro antes de continuar.",
                key="btn_column_check_continue_disabled",
            )
    with col2:
        if st.button("Cancelar", use_container_width=True, key="btn_column_check_cancel"):
            st.session_state.carga_fase = None
            st.session_state.column_check_result = None
            st.session_state.procesar_carga = False
            st.rerun()

    if not can_continue:
        st.info(
            "Use **Cancelar**, cambie los archivos de medición en la pestaña Archivos "
            "del formulario de arriba y vuelva a enviar."
        )
