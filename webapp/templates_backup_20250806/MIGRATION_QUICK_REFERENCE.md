# HTML to Modular CSS Migration - Quick Reference

## 🚀 **Start Here: Phase 1**

### **1. Update base.html**
```html
<!-- REMOVE this line -->
<link href="{{ url_for('static', path='/css/style.css') }}" rel="stylesheet">

<!-- KEEP this block for module-specific CSS -->
{% block extra_css %}{% endblock %}
```

### **2. Update index.html (Homepage)**
```html
{% extends "base.html" %}

{% block extra_css %}
<link href="{{ url_for('static', path='/css/homepage.css') }}" rel="stylesheet">
{% endblock %}
```

## 📋 **Module CSS Files & Class Prefixes**

| Module | CSS File | Class Prefix | Template Path |
|--------|----------|--------------|---------------|
| **Homepage** | `homepage.css` | `homepage-` | `index.html` |
| **AASX Processing** | `aasx.css` | `aasx-` | `aasx/index.html` |
| **Twin Registry** | `twin_registry.css` | `twin-registry-` | `twin_registry/index.html` |
| **AI RAG** | `ai_rag.css` | `ai-rag-` | `ai_rag/index.html` |
| **Federated Learning** | `federated_learning.css` | `federated-` | `federated_learning/index.html` |
| **Knowledge Graph** | `kg_neo4j.css` | `kg-` | `kg_neo4j/index.html` |
| **Physics Modeling** | `physics_modeling.css` | `physics-` | `physics_modeling/index.html` |
| **Certificate Manager** | `certificate-manager.css` | `certificate-` | `certificate_manager/index.html` |

## 🔄 **Template Update Pattern**

### **Step 1: Add CSS Import**
```html
{% extends "base.html" %}

{% block extra_css %}
<link href="{{ url_for('static', path='/css/{module_name}.css') }}" rel="stylesheet">
{% endblock %}
```

### **Step 2: Update Class Names**
```html
<!-- OLD -->
<div class="container dashboard">

<!-- NEW -->
<div class="{module-prefix}-container {module-prefix}-dashboard">
```

### **Step 3: Remove Inline Styles**
```html
<!-- OLD -->
<div style="background-color: #f8f9fa; padding: 1rem;">

<!-- NEW -->
<div class="{module-prefix}-section">
```

## 🎨 **Common Class Mappings**

### **Layout Classes**
| Old Class | New Class Pattern |
|-----------|-------------------|
| `container` | `{module-prefix}-container` |
| `row` | `{module-prefix}-row` |
| `col-md-*` | `{module-prefix}-col-md-*` |
| `card` | `{module-prefix}-card` |
| `btn` | `{module-prefix}-btn` |

### **Component Classes**
| Old Class | New Class Pattern |
|-----------|-------------------|
| `dashboard` | `{module-prefix}-dashboard` |
| `table` | `{module-prefix}-table` |
| `form` | `{module-prefix}-form` |
| `modal` | `{module-prefix}-modal` |
| `alert` | `{module-prefix}-alert` |

## 📁 **File Structure to Update**

```
webapp/templates/
├── base.html                    # ✅ Phase 1
├── index.html                   # ✅ Phase 1
├── aasx/index.html             # ✅ Phase 2.1
├── twin_registry/index.html    # ✅ Phase 2.2
├── ai_rag/index.html           # ✅ Phase 2.3
├── federated_learning/index.html # ✅ Phase 2.4
├── kg_neo4j/index.html         # ✅ Phase 2.5
├── physics_modeling/index.html # ✅ Phase 3.1
├── certificate_manager/index.html # ✅ Phase 3.2
├── auth/                       # ✅ Phase 4.1
├── flowchart/                  # ✅ Phase 4.2
├── qi_analytics/               # ✅ Phase 4.3
├── 404.html                    # ✅ Phase 5.1
├── 500.html                    # ✅ Phase 5.1
└── error.html                  # ✅ Phase 5.1
```

## ⚡ **Quick Commands**

### **Backup Templates**
```bash
cp -r webapp/templates webapp/templates_backup_$(date +%Y%m%d)
```

### **Find Inline Styles**
```bash
grep -r "style=" webapp/templates/
```

### **Find Old CSS References**
```bash
grep -r "style.css" webapp/templates/
```

### **Find Bootstrap Classes**
```bash
grep -r "class.*container\|class.*row\|class.*col-" webapp/templates/
```

## 🚨 **Common Issues & Solutions**

### **Issue 1: Bootstrap Classes**
**Problem**: Bootstrap classes like `container`, `row`, `col-*` might conflict
**Solution**: Keep Bootstrap classes, only prefix custom classes

```html
<!-- CORRECT -->
<div class="container aasx-dashboard">
<div class="row aasx-content">
<div class="col-md-6 aasx-panel">
```

### **Issue 2: Dynamic Classes**
**Problem**: JavaScript-generated classes
**Solution**: Update JavaScript to use new class names

```javascript
// OLD
element.className = 'dashboard';

// NEW
element.className = 'aasx-dashboard';
```

### **Issue 3: Component Templates**
**Problem**: Component templates in subdirectories
**Solution**: Update all component templates with same pattern

```bash
find webapp/templates/*/components/ -name "*.html" -exec echo "Update: {}" \;
```

## ✅ **Validation Checklist**

### **For Each Template:**
- [ ] CSS import added
- [ ] Class names updated with module prefix
- [ ] Inline styles removed
- [ ] Bootstrap classes preserved
- [ ] Component templates updated
- [ ] JavaScript references updated
- [ ] Visual appearance maintained
- [ ] Responsive design working

### **Global Validation:**
- [ ] All templates load without errors
- [ ] No console errors
- [ ] All interactive elements work
- [ ] Cross-browser compatibility
- [ ] Mobile responsiveness
- [ ] Performance maintained

## 📞 **Emergency Rollback**

If issues occur, restore from backup:
```bash
rm -rf webapp/templates
cp -r webapp/templates_backup_YYYYMMDD webapp/templates
```

---

**Last Updated**: January 2025  
**Use with**: HTML_CSS_MIGRATION_PLAN.md 